from django import forms


class QuillWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['style'] = 'display: none;'
        textarea = super().render(name, value, attrs, renderer)
        editor_id = f'quill-editor-{name}'
        return f'''
<div id="{editor_id}" style="height: 400px;">{value or ''}</div>
{textarea}
<script>
(function() {{
    var editor = document.getElementById('{editor_id}');
    var textarea = editor.nextElementSibling;
    var quill = new Quill('#{editor_id}', {{ theme: 'snow' }});
    if (textarea.value) {{
        quill.root.innerHTML = textarea.value;
    }}
    quill.on('text-change', function() {{
        textarea.value = quill.root.innerHTML;
    }});
}})();
</script>
'''
