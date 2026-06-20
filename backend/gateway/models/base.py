from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    """Менеджер по умолчанию, возвращающий только неудаленные объекты."""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteModel(models.Model):
    """
    Абстрактная модель с поддержкой Soft Delete.
    Автоматически скрывает удаленные записи.
    """
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        """Переопределяем метод delete() для выполнения soft delete."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        """Восстанавливает запись."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    class Meta:
        abstract = True
