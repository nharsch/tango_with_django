import os

from django.contrib.auth.models import User
from django import forms
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory

import xlrd

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

class ManifestInitForm(forms.Form):
    title = forms.CharField(max_length=128, help_text="Please enter the title you want to add")

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
        # exclude = ('category',)
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

class FullPageForm(PageForm):
    '''form page above with category dropdown'''
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                      to_field_name='slug')


class PageBulkForm(forms.Form):
    '''form to create several pages at once'''
    category_choices = forms.ModelMultipleChoiceField(queryset=Category.objects.all())
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page")
    url = forms.URLField(max_length=200, 
                         help_text="Please ener the URL of the page",
                         widget=forms.widgets.TextInput,)
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

PageFormSet = formset_factory(FullPageForm, extra=0)

class UploadForm(forms.Form):
    '''
    will accept XLS, clean and collect values as list of dicts
    '''

    spreadsheet = forms.FileField(label='Upload Spreadsheet')

    def clean_spreadsheet(self):
        spreadsheet = self.cleaned_data.get('spreadsheet', None)
        if spreadsheet is not None:
            _, ext = os.path.splitext(spreadsheet.name)
            if ext not in ('.xls', '.xlsx'):
                raise forms.ValidationError('File should be in an Excel (.xls or .xlsx) format.')
            try:
                spreadsheet = xlrd.open_workbook(filename=spreadsheet.name,
                                                 file_contents=spreadsheet.read())
            except:
                raise forms.ValidationError('File is not a valid Excel file.')
            return spreadsheet
    
    def clean(self):
        cleaned_data = self.cleaned_data 
        if self.errors:
            return cleaned_data
        workbook = cleaned_data['spreadsheet']
        worksheet = workbook.sheet_by_index(0)

        # our manifest of jobs
        cleaned_data['updates'] = []
        # Row 1 is labels
        for i in range(1, worksheet.nrows):
            columns = worksheet.row_len(i)
            row = worksheet.row_values(i, start_colx=0, end_colx=columns)
            try:
                # asset translater defined below
                updates = self.translate_row(i, row)
            except forms.ValidationError as e:
                self.add_error(None, e)
            else:
                if updates is not None:
                    cleaned_data['updates'].append(updates)
        if not (self.errors or cleaned_data['updates']):
            raise forms.ValidationError('The spreadsheet does not contain any assets to update.')
        return cleaned_data

    # ok, now the hard part
    def translate_row(self, index, row):
        '''translates a row from the template to a tuple of an asset and
        the related data dictionary to update.'''
        
        # build empty jobs for empty lines
        if not row or not row[0]:
            return (None, {})
        
        if len(row) != 3:
            raise forms.ValidationError('Row {}: Does not have all columns filled out')

        category, title, url = row
        
        # let's return the row dict and validate it on the next post method ot
        # the upload view
        return {'category':category, 'title':title, 'url':url}

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

