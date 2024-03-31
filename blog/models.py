import random

from django.db import models
from django.db.models import Model, Count, Q, Prefetch

from utilities.common import clock, rnd_string, rnd_number


def adjust_posts_with_tags():
    for tag in Tag.objects.all():
        while not [p for p in Post.objects.all() if tag in p.tags.all()]:
            Post.create_n_post(5)


class Tag(Model):
    class Meta:
        verbose_name = 'Тег'
        ordering = ['name']

    TAG_SIZE = 20

    name = models.CharField(max_length=TAG_SIZE, blank=False, null=False)

    @classmethod
    def get_n_tag_randomly(cls, n):
        tag_qs = cls.objects.all()
        return random.sample(set(tag_qs), n)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Post(Model):
    class Meta:
        verbose_name = 'Пост'
        ordering = ['created']

    tags = models.ManyToManyField(Tag, related_name='posts')
    name = models.CharField(max_length=20, blank=False, null=False)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'id:{self.pk},  name:{self.name}, tags: {self.tags.only("id")}'

    # @clock
    # def get_similar_by_n_tag(self, similarity=1):
    #     qs = self.__class__.objects.prefetch_related('tags').all()
    #     res = [p for p in qs if (p.tags.all() & self.tags.all()).count() == similarity]
    #     return res

    @classmethod
    def create_n_post(cls, n):
        for _ in range(n):
            name = f"{rnd_string(4)} - {rnd_number(4)}"
            post = cls.objects.create(name=name)
            tag_numb = random.randint(0, 10)
            random_tags = Tag.get_n_tag_randomly(tag_numb)
            post.tags.add(*random_tags)
        return

    def get_tags_count(self):
        return self.tags.all().count

    @clock
    def get_similar_no_less_than_n_tag(self, similarity=1):
        """ вернет список объектов Post у к-х
            количество общих, с данной записью, тегов равно similarity
        """

        qs = Post.objects.annotate(cmn_tags_cnt=Count('tags',
                                                      filter=Q(tags__in=self.tags.all()))) \
            .filter(Q(cmn_tags_cnt__gte=similarity) & ~Q(pk=self.pk)).values('pk', 'cmn_tags_cnt')

        print(qs.query)
        return qs

    @clock
    def x_get_similar_by_n_tag(self, similarity=1):
        qs = self.__class__.objects.prefetch_related(
            Prefetch(
                lookup='tags',
                queryset=Tag.objects.filter(pk__in=self.tags.all()),
                to_attr='same_tags')
        ).annotate(c=Count('same_tags')).filter(c=similarity)
        return qs

    @clock
    def get_n_post_most_similar_by_tags_to_self(self, ret_count=0):

        qs = self.__class__.objects.prefetch_related(
            Prefetch(
                lookup='tags',
                queryset=Tag.objects.filter(pk__in=self.tags.all()),
                to_attr='same_tags')
        ).all()
        res = [p for p in qs.order_by('same_tags__count').desc()]
        if ret_count:
            res = res[:ret_count]
        return res


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
        related_name='membership_invites',
    )
    invite_reason = models.CharField(max_length=64)
