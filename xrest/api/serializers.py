from rest_framework import serializers

from .models import SomeFile

import mimetypes
import os


class SomeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SomeFile
        fields = ('file',
                  )

    def create(self, validated_data):
        instance = SomeFile.objects.create(**validated_data)
        instance.name = os.path.basename(instance.file.name)
        instance.size = instance.file.size
        instance.mime_type = mimetypes.guess_type(instance.file.path)[0]
        instance.ext = os.path.splitext(instance.file.name)[1]

        instance.save()
        return instance

    def update(self, instance, validated_data):
        file = validated_data.get('file')
        old_file = instance.file

        file.name = old_file.name
        old_file.delete()

        instance.file = file
        instance.size = instance.file.size
        instance.mime_type = mimetypes.guess_type(instance.file.path)[0]
        instance.ext = os.path.splitext(instance.file.name)[1]

        instance.save()
        return instance


class SomeFileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SomeFile
        fields = ('id',
                  'name',
                  )


class SomeFileMetaSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S %z')
    modified = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S %z')

    class Meta:
        model = SomeFile
        fields = ('name',
                  'size',
                  'mime_type',
                  'ext',
                  'created',
                  'modified',
                  )
