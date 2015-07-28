from django import forms
from django.contrib.auth.models import User
from django.forms.models import modelformset_factory
from rango.models import Page, Category, UserProfile

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           help_text="Please enter the category name:"
                           )
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # An inline class to provide additional information on the form.
    class Meta:
    # Provide an association between the ModelForm and a model
        model = Category
        field = ('name',)

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page")
    url = forms.URLField(max_length=200, 
                         help_text="Please ener the URL of the page",
                         widget=forms.widgets.TextInput,)
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
    # Provide an association between the ModelForm and a model
        model = Page

        # What fields do we want to include in our form?
        # This way we don't need every field in the model present
        # Some fields may allow NULL values, so we may not want to includie them...
        # we can either exclude the category field from the form,
        exclude = ('category',)
        #or specify the fields to include (i.e. not include the category field)
        #fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If url is not empty and doesn't start with 'http://', prepend with 'http://'
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data

PageFormSetBase = modelformset_factory(
    Page, extra=0, fields=('title', 'category', 'url', 'views')
)

class PageBulkForm(forms.Form):
    '''form to create several pages at once'''
    category_choices = forms.ModelMultipleChoiceField(queryset=Category.objects.all())
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page")
    url = forms.URLField(max_length=200, 
                         help_text="Please ener the URL of the page",
                         widget=forms.widgets.TextInput,)
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    website = forms.URLField(max_length=200, 
                             help_text="Please ener the URL of the page",
                             widget=forms.widgets.TextInput,)
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')

    def clean(self):
        cleaned_data = self.cleaned_data
        website = cleaned_data.get('website')
        if website and not website.startswith('http://'):
            website = 'http://' + website
            cleaned_data['website'] = website

        return cleaned_data

