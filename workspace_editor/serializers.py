from rest_framework import serializers
from workspace_editor.models import Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    visible_for = serializers.SerializerMethodField("get_visible_for")
    editable_by = serializers.SerializerMethodField("get_editable_by")

    def get_visible_for(self, obj):
        return "; ".join(obj.visible_for.all().values_list('email', flat=True))

    def get_editable_by(self, obj):
        return "; ".join(obj.editable_by.all().values_list('email', flat=True))

    class Meta:
        model = Workspace
        exclude = ("owner",)
