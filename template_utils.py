from flask import Response, current_app, stream_with_context


def stream_template(template_name: str, **context):
    template = current_app.jinja_env.get_template(template_name)
    return Response(stream_with_context(template.stream(context)), mimetype='text/html')
