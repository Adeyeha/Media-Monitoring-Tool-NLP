from django import forms
from .models import templateupload

class fileuploadform(forms.Form):
    # file = forms.FileField(initial='nothing').
    file = forms.FileField(label='File',widget=forms.FileInput(attrs={'class': 'form-control form-control-sm'}))

class details(forms.Form):
    search_subject = forms.CharField(label='Subject',widget=forms.TextInput(attrs={'readonly':'readonly'}),required=False)
    title = forms.CharField(label='Title',widget=forms.TextInput(attrs={'readonly':'readonly'}),required=False)
    # source = forms.CharField(label='Source',widget=forms.TextInput(),required=False)
    url = forms.CharField(label='URL',widget=forms.TextInput(attrs={'readonly':'readonly'}),required=False)
    summary=forms.CharField(label='Summary',widget=forms.Textarea(attrs={'readonly':'readonly'}),required=False)
    newsdate = forms.CharField(label='News Date',widget=forms.TextInput(attrs={'readonly':'readonly'}),required=False)

class templateuploadform(forms.ModelForm):
    # file = forms.FileField(initial='nothing').
    # file = forms.FileField(label='File',widget=forms.FileInput(attrs={'class': 'form-control form-control-sm'}))
    class Meta:
        model = templateupload
        fields = ['filepath', 'purpose']

    def __init__(self, *args, **kwargs):
        super(templateuploadform, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "form-control form-control-sm"
            # field.required = True
