import os
from label_studio_sdk.client import LabelStudio


LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
API_KEY = os.getenv('LABEL_STUDIO_API_KEY')


def get_or_create_al_project(ls: LabelStudio):
    target_title = 'AL Project Created from SDK'
    # Try to find existing project by title
    for p in ls.projects.list():
        if getattr(p, 'title', '') == target_title:
            return p
    # Create if not found
    return ls.projects.create(
        title=target_title,
        label_config="""
        <View>
        <Text name="text" value="$text"/>
        <Choices name="sentiment" toName="text" choice="single" showInLine="true">
            <Choice value="Positive"/>
            <Choice value="Negative"/>
            <Choice value="Neutral"/>
        </Choices>
        </View>
        """,
    )


def main() -> None:
    ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)
    project = get_or_create_al_project(ls)

    sample_texts = [
        'I love this product!',
        'This is terrible and disappointing',
        "Meh, it's okay I guess",
        'Absolutely fantastic experience',
        'Not good, would not recommend',
    ]
    # Create tasks
    created = []
    for text in sample_texts:
        t = ls.tasks.create(project=project.id, data={'text': text})
        created.append(t)

    # Add annotations to first 3 tasks
    labels = ['Positive', 'Negative', 'Neutral']
    for task, label in zip(created[:3], labels):
        ls.annotations.create(
            id=task.id,
            result=[
                {
                    'from_name': 'sentiment',
                    'to_name': 'text',
                    'type': 'choices',
                    'value': {'choices': [label]},
                }
            ],
            was_cancelled=False,
        )
    print(
        f'Prepopulated project {project.id} with {len(created)} tasks and 3 annotations'
    )


if __name__ == '__main__':
    main()
