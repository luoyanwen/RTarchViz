# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import permalink
from django.template.defaultfilters import truncatechars

class PostManager(models.Manager):
  """
  Defining custom Manager methods
  """
  def published(self):
    """ select only published posts """
    return self.get_queryset().filter(status="published")

class Post(models.Model):
  """
  Defining Blog's Post models
  """

  # CHOICES:
  CATEGORY_CHOICES = (
    ('news', 'News'),
    ('tutorial', 'Tutorial')
  )
  STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published')
  )

  # DATABASE FIELDS:
  # author is linked to a registered staff user, via the User model in the accounts app.
  author = models.ForeignKey(settings.AUTH_USER_MODEL)
  title = models.CharField(max_length=200, unique=True)
  # slug is generated from the title
  slug = models.SlugField(editable=False, max_length=200, unique=True)
  content = models.TextField(max_length=10000)
  # identify when post was created
  created_date = models.DateTimeField(editable=False, default=timezone.now)
  # set publish date initially to blank and null as drafts are allowed
  # published date will be set once post is published
  published_date = models.DateTimeField(editable=False, blank=True, null=True)
  # record when a published post is last edited
  updated_date = models.DateTimeField(editable=False, blank=True, null=True)
  # record how often a post is seen
  view_count = models.IntegerField('views', editable=False, default=0)
  # set post's category
  category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='news')
  # set post's status (draft or published)
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
  # add images to a post (stores relative path to image)
  image = models.ImageField(upload_to="images", blank=True, null=True)

  # MANAGERS:
  objects = PostManager()
  
  # META CLASS:
  class Meta:
    """specify global meta options for model"""
    ordering = ('-published_date',) # set default ordering of the objects

  # TO STRING METHOD:
  def __unicode__(self):
    """identify blog entries by their title for admin page """
    return self.title

  # SAVE METHOD:
  def save(self, *args, **kwargs):
    """
    overwrite Model save method to 
    1. automatically generate a slug from post's title
    2. set published_date with current date & time when post's status is initially
       changed from 'draft' to 'published'
    3. set updated_date with current date & time if published_date already set
    """
    self.slug = self.get_slug()
    if self.status == 'published' and self.published_date is None or '':
      self.published_date = timezone.now()
    elif self.status == 'published' and self.published_date is not None or '':
      self.updated_date = timezone.now()
    super(Post, self).save()

  # ABSOLUTE URL METHODS:
  @permalink
  def get_post_detail_url(self):
    return ('post_detail', [self.published_date.year,
                            self.published_date.month,
                            self.slug])

  # OTHER METHODS:
  def get_slug(self):
    """
    create a slug from post's title
    """
    slug = slugify(self.title)
    return slug
 
  def get_author(self):
    """
    get user's full name or username
    """
    if self.author.first_name and self.author.last_name:
      return "%s %s" % (self.author.first_name, self.author.last_name)
    else: 
      return self.author.username

  def get_short_content(self):
    '''get a truncated version of a post's content'''
    return truncatechars(self.content, 200)

  