def underscore_to_pascalcase(value):

    def pascalcase():
        while True:
            yield str.capitalize

    c = pascalcase()
    new_name = "".join(c.next()(str(x)) if x else '_' for x in value.split("_"))
    return new_name
