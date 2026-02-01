from django import forms
from .models import Motion, MotionResponse, Comment


class MotionForm(forms.ModelForm):
    class Meta:
        model = Motion
        fields = [
            'title', 'evidence', 'proposed_action', 'resource_ask',
            'success_measures', 'jurisdiction', 'safeguarding_considerations',
            'inclusion_considerations', 'status'
        ]
        widgets = {
            'evidence': forms.Textarea(attrs={'rows': 4}),
            'proposed_action': forms.Textarea(attrs={'rows': 3}),
            'resource_ask': forms.Textarea(attrs={'rows': 3}),
            'success_measures': forms.Textarea(attrs={'rows': 3}),
            'safeguarding_considerations': forms.Textarea(attrs={'rows': 2}),
            'inclusion_considerations': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('draft', 'Save as Draft'),
            ('published', 'Publish to Feed'),
        ]
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent bg-white'
            else:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent'


class MotionResponseForm(forms.ModelForm):
    class Meta:
        model = MotionResponse
        fields = ['decision', 'reasons', 'delivery_plan', 'milestones', 'due_date', 'alternative_pathway']
        widgets = {
            'reasons': forms.Textarea(attrs={'rows': 4}),
            'delivery_plan': forms.Textarea(attrs={'rows': 3}),
            'milestones': forms.Textarea(attrs={'rows': 3}),
            'alternative_pathway': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent bg-white'
            else:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share your thoughts on this motion...',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent'
            })
        }
