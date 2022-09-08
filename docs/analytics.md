# Analytics

We store information about certain events in our database.

## Deletion of data

### When a user deletes their account, we record:

- the user id
- the ids of their data donation (and the corresponding campaigns)
- the timestamp of deletion

All other data gets deleted.

### When a user deletes a single donation, we record:

- the donation id
- the user
- the campaign
- the timestamp of deletion

## Exceptions

We store all view-releated exceptions (permissioned denied, rate limited).
