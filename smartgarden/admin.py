from django.contrib import admin

from smartgarden.models import *

admin.site.register(User)
admin.site.register(Circuit)
admin.site.register(Activation)
admin.site.register(ScheduledOneTimeActivation)
admin.site.register(ScheduledActivation)
