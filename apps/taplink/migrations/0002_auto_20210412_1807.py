# Generated by Django 2.2 on 2021-04-12 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taplink', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Messanger',
            new_name='Messenger',
        ),
        migrations.AlterModelOptions(
            name='body',
            options={'verbose_name': 'Text', 'verbose_name_plural': 'Texts'},
        ),
        migrations.AlterModelOptions(
            name='deck',
            options={'verbose_name': 'Deck', 'verbose_name_plural': 'Decks'},
        ),
        migrations.AlterModelOptions(
            name='messenger',
            options={'verbose_name': 'Messenger', 'verbose_name_plural': 'Messengers'},
        ),
        migrations.RenameField(
            model_name='messenger',
            old_name='messanger',
            new_name='messenger',
        ),
    ]
