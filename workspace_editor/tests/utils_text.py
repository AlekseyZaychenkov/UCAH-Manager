
def parse_tags_from_input(input_str: str):
    tags = []
    for tag in input_str.strip().split():
        # TODO: checking for existing posts with this tag in selected resource
        tag = ''.join(tag.strip('_'))
        if tag not in tags:
            tags.append(tag)

    return ', '.join(tags)

def prepare_tags_for_edit_form(input_str: str):
    return '#' + ' #'.join(input_str)
