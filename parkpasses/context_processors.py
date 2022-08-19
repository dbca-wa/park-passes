from parkpasses.settings import (
    BUILD_TAG,
    KMI_SERVER_URL,
    template_group,
    template_title,
)


def parkpasses_template_url(request):
    return {
        "KMI_SERVER_URL": KMI_SERVER_URL,
        "template_group": template_group,
        "template_title": template_title,
        "build_tag": BUILD_TAG,
    }
