from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Case,
    CaseType,
    Entity,
    ReceivedMessage,
    SentMessage,
    ExternalSupport,
)

admin.site.register(CaseType, SimpleHistoryAdmin)
admin.site.register(Case, SimpleHistoryAdmin)
admin.site.register(ReceivedMessage, SimpleHistoryAdmin)
admin.site.register(SentMessage, SimpleHistoryAdmin)
admin.site.register(Entity, SimpleHistoryAdmin)
admin.site.register(ExternalSupport, SimpleHistoryAdmin)
