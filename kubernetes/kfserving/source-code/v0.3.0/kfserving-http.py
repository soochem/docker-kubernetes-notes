class ExplainHandler(HTTPHandler):
    def post(self, name: str):
        model = self.get_model(name)
        try:
            body = json.loads(self.request.body)
        except json.decoder.JSONDecodeError as e:
            raise tornado.web.HTTPError(
                status_code=HTTPStatus.BAD_REQUEST,
                reason="Unrecognized request format: %s" % e
            )
        request = model.preprocess(body)
        request = self.validate(request)
        response = model.explain(request)
        response = model.postprocess(response)
        self.write(response)