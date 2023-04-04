from datetime import datetime, date, timedelta
import logging
from django import forms
from django.http import QueryDict

from loader.models import Compilation
from workspace_editor.models import Workspace, Blog, Event, EventRules, PostingTime, Schedule, EventArchived
from workspace_editor.utils.utils import move_post_to_compilation, log

log = logging.getLogger(__name__)


class EventAutoCreateForm(forms.ModelForm):
    blogs       = forms.ModelMultipleChoiceField(Blog.objects.all(), required=False)
    post_id     = forms.CharField()
    datetime    = forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M"])

    def save_copied_post(self, workspace_id, recipient_compilation_id, delete_original_post=False):
        self.instance.post_id = move_post_to_compilation(workspace_id,
                                                         recipient_compilation_id,
                                                         self.data.get("post_id"),
                                                         delete_original_post)
    def set_datetime(self, datetime_slot: datetime):
        event = self.instance
        event.datetime = datetime_slot

    def set_schedule(self, schedule):
        event = self.instance
        event.schedule = schedule

    class Meta:
        model = Event
        exclude = ('schedule', )


# TODO: fix error "sqlite3.OperationalError: sub-select returns 10 columns - expected 1"
def create_event(workspace: Workspace, time_slot, post_id: int):
    blogs = Blog.objects.filter(workspace=workspace)
    query_dict = QueryDict('', mutable=True)
    query_dict.update({'blogs': blogs, 'post_id': post_id})
    form = EventAutoCreateForm(query_dict)
    log.info(f"Checking form:")
    log.info(form)
    if form.is_valid():
        try:
            form.save_copied_post(workspace_id=workspace.workspace_id,
                                  recipient_compilation_id=workspace.scheduled_compilation_id,
                                  delete_original_post=True)
            form.set_datetime(time_slot)
            form.set_schedule(workspace.schedule)
            log.info(f"Creating an event")
            form.save()
        except Exception as e:
            log.error(f"Error during creation event!:\n{str(form)} \n{e}")
    else:
        log.error(form.errors.as_data())


def __get_first_free_slot(day_slots, current_date, schedule):
    for slot in day_slots:
        checking_slot = datetime(year=current_date.year,
                                 month=current_date.month,
                                 day=current_date.day,
                                 hour=slot.hour,
                                 minute=slot.minute,
                                 second=slot.second)

        if Event.objects.filter(schedule=schedule, datetime=checking_slot.astimezone()).count() == 0:
            return checking_slot


# TODO: consider combining with __get_free_slot and return only first date
def __get_all_slots_for_date(event_rules: EventRules, priority: int, current_date: date):
    day_slots = list()
    datetime_now = datetime.now()
    posting_times = PostingTime.objects.filter(event_rules=event_rules, priority=priority)

    for posting_time in posting_times:
        if current_date == datetime_now.date():
            if posting_time.time > datetime_now.time():
                day_slots.append(posting_time.time)
        else:
            day_slots.append(posting_time.time)

    return day_slots


def __calculate_datetime_for_distribution_n_per_day(event_rules: EventRules,
                                                    datetime_now: datetime,
                                                    schedule,
                                                    slots_on_lowest_priority: int):

    current_date = date(year=datetime_now.year, month=datetime_now.month, day=datetime_now.day)
    while True:
        for priority in range(1, slots_on_lowest_priority + 1):
            day_slots = __get_all_slots_for_date(event_rules, priority, current_date)

            return __get_first_free_slot(day_slots=day_slots, current_date=current_date, schedule=schedule)

        current_date = current_date + timedelta(days=1)


def __get_day_numbers(first_day, last_day):
    if last_day - first_day == 0:
        return []
    elif last_day - first_day == 1:
        return [first_day]
    else:
        return [int((last_day - first_day) / 2 + first_day)] \
            + __get_day_numbers(first_day, int((last_day - first_day) / 2 + first_day)) \
            + __get_day_numbers(int((last_day - first_day) / 2 + first_day) + 1, last_day)


def __calculate_datetime_for_time_range(distribution_type_code: float,
                                        event_rules: EventRules,
                                        datetime_now: datetime,
                                        schedule,
                                        slots_on_lowest_priority: int):

    first_date = date(year=datetime_now.year, month=datetime_now.month, day=datetime_now.day)

    target_event_density = distribution_type_code
    total_days_to_fill = int(1 / target_event_density + 0.5)
    first_day = 0
    end_day = total_days_to_fill

    for priority in range(1, slots_on_lowest_priority + 1):
        print(f"priority: {priority}")

        day_numbers = __get_day_numbers(first_day, end_day)
        for day_number in day_numbers:
            print(f"day_number: {day_number}")

            slots_for_date = __get_all_slots_for_date(event_rules=event_rules,
                                                      priority=priority,
                                                      current_date=first_date + timedelta(days=day_number))

            current_date = date(year=datetime_now.year, month=datetime_now.month, day=datetime_now.day + day_number)

            free_slot = __get_first_free_slot(day_slots=slots_for_date, current_date=current_date, schedule=schedule)

            if free_slot:
                print(f"<== free_slot: {free_slot} ==>")
                return free_slot

    return None


def calculate_datetime_from_event_rules(schedule: Schedule):
    workspace = Workspace.objects.get(schedule=schedule)
    move_obsolete_events_to_schedule_archive(workspace)
    slots_on_lowest_priority = 6

    event_rules = workspace.event_rules
    distribution_type_code = event_rules.distribution_type

    datetime_now = datetime.now()


    # N per day
    if distribution_type_code >= 1:
        return __calculate_datetime_for_distribution_n_per_day(event_rules=event_rules,
                                                               datetime_now=datetime_now,
                                                               schedule=schedule,
                                                               slots_on_lowest_priority=slots_on_lowest_priority)

    # over N days/weeks/months
    else:
        return __calculate_datetime_for_time_range(distribution_type_code=distribution_type_code,
                                                   event_rules=event_rules,
                                                   datetime_now=datetime_now,
                                                   schedule=schedule,
                                                   slots_on_lowest_priority=slots_on_lowest_priority)


# @transaction.atomic
def fill_schedule(schedule: Schedule):
    workspace = Workspace.objects.get(schedule=schedule)

    while True:
        free_slot = calculate_datetime_from_event_rules(schedule)
        post_ids = Compilation.objects.get(id=workspace.main_compilation_id).post_ids
        post_id = post_ids[0] if post_ids else None

        if free_slot and post_id:
            create_event(workspace, free_slot, post_id)
        else:
            break


def move_obsolete_events_to_schedule_archive(workspace: Workspace):
    obsolete_events = Event.objects.filter(schedule=workspace.schedule, datetime__lt=datetime.now())

    for event in obsolete_events:
        event_archive = EventArchived(schedule=workspace.schedule_archive,
                                      post_id=event.post_id,
                                      datetime=event.datetime)
        event_archive.save()
        event.delete()
