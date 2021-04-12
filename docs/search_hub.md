# Searching through External Support and Case Types in the Hub

We are using [Django's Wrapper around Postgres' Fulltext search](https://docs.djangoproject.com/en/3.1/ref/contrib/postgres/search/).

## External Support

Set the Airtable keys in settings and then import data:

```
./manage.py importsupport
```

1. Filter by tag

```
/api/externalsupport/?tag=thetag
```

2. Search by query

```
/api/externalsupport/?q=thequery
```

3. Both

```
/api/externalsupport/?tag=thetag&q=thequery
```

## Case Types

1. Filter by tag

```
/api/casetype/?tag=thetag
```

2. Search by query

```
/api/casetype/?q=thequery
```

3. Both

```
/api/casetype/?tag=thetag&q=thequery
```
