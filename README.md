# An Effect Handler App

Let's start with something terse: this app routes data, representing `effects`, to `effects handlers` which then perform the actions necessary to action those effects. 

Terse is often accurate but impenetrable, so let's give an overview ... 

In re-frame, when an event "happens", an event handler is used to compute how the app should respond to that event and it is expected to produce data which declaratively describes how the world should be changed. This data must then be actioned, which is where `effect handlers` come in.  Working from the descriptions provided, they perform the dirty work of mutating the world. 

This Django app supports a very similar process at the systems level (rather than the re-frame level). Parts of the system often need to make effectful changes to the world, like sending email or writing blobs to S3. This app provides a mechanism by which those sorts of effects can be actioned. It is particularly useful when the effects involve performing asynconous actions.

The mechanism:
  - effects are created by adding a row to the table XXX 
  - each row represents one `effect` and each has an identifying `kind` and a `JSON payload`  (columns in the Table)
  - Hasura notices each new row added and it is configured to POST to a webhook 
  - The webhook endpoint is this Django app (see (`effect_handler.views.new_effect_handler`)
  - when this endpoint is POSTed to, it will action the effect described by the data in the row
  - Using the effect's `kind`, this app must first find the right, registered `effects handler` and then call it
  - that handler is responsible for interpreting the `payload` supplied and performing the action it describes
  - when the task is completed, the handler must see to it that `completion information` to be written 
    back into the effects table.

Benefits:
1. The effects table acts as an inspectable audit trail, capturing all the changed requested. Effects are described as data.
2. Any part of the system, including the CLJS client can cause effects by simply saving data into the effects table
3. The part of the system requesting the effect is decoupled from that part which actions it
4. The part of the system requesting the effect does not need to worry about retries or failure. Fire and forget
5. The handling of an effect can be handled synchronously or delegated to a Celery task via a chained callback. 


XXX what of the following have I missed out ....

## The good flow

  * Hasura mutation of effect_handler_fxtable
      * contains an `kind` and a `payload`
  * Hasura webhook posts to the `effect_handler.views.new_effect_handler` endpoint
     * end point recieves the event and processes `kind` and `payload`
  * Based on the `kind` the router looks at registered fx and calls the 
    registered function with the payload and the callback to write completion 
    information
  * The django handler can then deal with the fx synchronously, or call a 
    celery task with a chained callback.
  * After the task has completed the callback will write the completion time
    and the completion payload to the fx_table

## The bad flow

TODO

## api calls

### register_fx

This function will registor an effect with the effect handler, it takes
    
  * kind : str : arguement that will match the `kind` column in the fx_table
  * fx: callable : argument that will be called when the fx is triggered

### signature of callable

The `fx` callable should take 2 arguements the payload (normally a json map of
parameters) and the completion callback. 

The return value of the callable can be passed directly to the completion
callback, or an additional celery task can be fired off to to the work


# Examples

## register an fx (async)

    def publish_rateset(payload: dict, callback=None):
        rateset_id = payload['RATESET']
        log.info("Publishing %s", rateset_id)
        # check if rateset exists
        rs = get_object_or_404(RateSet, pk=rateset_id)
        rs.status = StatusChoice.PUBLISHING.value
        rs.save()
        upload_rateset.apply_async([rs.pk], link=callback)
        return rateset_id

    register_fx("publish_rateset", publish_rateset)
    
Note that `publish_rateset` validates the rateset id before starting an task
'upload_rateset` that does the real work. In this case the return value of 
publish_rateset will be not used.

## register an fx (async)

    def publish_rateset(payload: dict, callback=None):
        rateset_id = payload['RATESET']
        log.info("Publishing %s", rateset_id)
        # check if rateset exists
        rs = get_object_or_404(RateSet, pk=rateset_id)
        rs.status = StatusChoice.PUBLISHING.value
        rs.save()
        ret = upload_rateset(rs.pk)
        if callback:
            callback.s(ret).get()
        return rateset_id

    register_fx("publish_rateset", publish_rateset)
    
non Async version of above.
