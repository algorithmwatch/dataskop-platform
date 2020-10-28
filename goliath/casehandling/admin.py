from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Case, CaseType, Entity, ReceivedMessage, SentMessage

admin.site.register(CaseType, SimpleHistoryAdmin)
admin.site.register(Case)
admin.site.register(ReceivedMessage)
admin.site.register(SentMessage)
admin.site.register(Entity)
