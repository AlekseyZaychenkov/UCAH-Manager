from rest_framework import serializers
from workspace_editor.models import Calendar
from loader.models import PostEntry


class CalendarSerializer(serializers.ModelSerializer):
    visible_for = serializers.SerializerMethodField("get_visible_for")
    editable_by = serializers.SerializerMethodField("get_editable_by")

    def get_visible_for(self, obj):
        return "; ".join(obj.visible_for.all().values_list('email', flat=True))

    def get_editable_by(self, obj):
        return "; ".join(obj.editable_by.all().values_list('email', flat=True))

    class Meta:
        model = Calendar
        exclude = ("owner",)

# class PostSerializer(serializers.ModelSerializer):
#
#     title  = serializers.SerializerMethodField("get_title")
#     start = serializers.SerializerMethodField("get_start")
#     end = serializers.SerializerMethodField("get_end")
#
#     def get_title(self, obj):
#         return obj.name
#
#     def get_start(self,obj):
#         return obj.start_date
#
#     def get_end(self,obj):
#         return obj.end_date
#
#     class Meta:
#         model = PostEntry
#         fields = ("title","start","end","icon","event_id","event_type")
