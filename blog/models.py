from django.db import models
from django.db.models import Model, Count, F, Q, Sum, Case, When, Value, IntegerField, Prefetch


class Tag(Model):
    class Meta:
        verbose_name = 'Тег'
        ordering = ['name']

    TAG_SIZE = 20

    name = models.CharField(max_length=TAG_SIZE, blank=False, null=False)

    def __repr__(self):
        return self.name


class Post(Model):
    class Meta:
        verbose_name = 'Пост'
        ordering = ['created']

    tags = models.ManyToManyField(Tag, related_name='posts')
    name = models.CharField(max_length=20, blank=False, null=False)
    created = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f"{self.name}, tags: {self.tags.all()}"

    # def orm_get_similar_by_n_tag(self, similarity_rank=1, returned_count=1):
    #     xposts = self.__class__.objects.prefetch_related('tags').all()
    #     res = [p for p in xposts if (p.tags.all() & self.tags.all()).count() == similarity_rank]
    #     return res[:returned_count] if len(res) > returned_count else res

    def orm_get_similar_by_n_tag(self, similarity_rank=1, returned_count=1):
        xposts = self.__class__.objects.prefetch_related(
            Prefetch('tags', Tag.objects.filter(pk__in=self.tags), 'sim_tags')
        )
        res = [p for p in xposts.all() if p.sim_tags.count() == similarity_rank]
        return res[:returned_count] if len(res) > returned_count else res

    # def orm_get_similar_by_n_tag(self, similarity_rank=1, returned_count=1):
    #     xposts = self.__class__.objects.annotate(
    #         similarity=F("tags.all()").aggregate(similar_tag_count=Sum(
    #             Case(
    #                 When(id__in=self.tags.all().values_list("id", flat=True), then=Value(1)),
    #                 default=Value(0),
    #                 output_field=IntegerField(),
    #             )
    #         ))['similar_tag_count']
    #     )
    #     res = [p for p in xposts if p.similarity == similarity_rank]
    #     return res[:returned_count] if len(res) > returned_count else res


class Person(models.Model):
    name = models.CharField(max_length=50)


class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(
        Person,
        through='Membership',
        through_fields=('group', 'person'),
    )


class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    inviter = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="membership_invites",
    )
    invite_reason = models.CharField(max_length=64)
