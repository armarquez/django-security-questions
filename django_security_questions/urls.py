from .compat import url, patterns


urlpatterns = patterns('',
    url(
        regex=r'^questions/add/$',
        view='add',
        name='questions_add'
    ),
    url(
        regex=r'^questions/change/$',
        view='change',
        name='questions_change'
    ),
)