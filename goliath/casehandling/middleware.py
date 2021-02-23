def reverse_proxy_adapt_ip(get_response):
    """
    Set the real IP address of the user if Django runs behind reverse proxy
    https://django-ratelimit.readthedocs.io/en/latest/security.html#middleware
    """

    def process_request(request):
        if "HTTP_X_FORWARDED_FOR" in request.META:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            request.META["REMOTE_ADDR"] = x_forwarded_for

        return get_response(request)

    return process_request
