### need to specify host!

it gets blocked unless you set server name to localhost
(ipv6 issue? I have localhost whitelisted in settings)

```python
c = Client(SERVER_NAME='localhost')
```

### header nonsense

for the client to treat something as a header, it must start with `HTTP_`... ugh

```python
c.get("/more", {'datastar': "{\"lastId\":290}"}, **{'HTTP_Datastar-Request': 'true'})
```