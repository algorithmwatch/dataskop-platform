from django.contrib import admin

from .models import CaseType, Case, ReceivedMessage, SentMessage, Entity

admin.site.register(CaseType)
admin.site.register(Case)
admin.site.register(ReceivedMessage)
admin.site.register(SentMessage)
admin.site.register(Entity)
