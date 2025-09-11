# Js ts sdk ref

# Js ts sdk ref
**[@langchain/langgraph-sdk](https://github.com/langchain-ai/langgraph/tree/main/libs/sdk-js)**
---
## [@langchain/langgraph-sdk](https://github.com/langchain-ai/langgraph/tree/main/libs/sdk-js)[¶](#langchainlanggraph-sdk "Permanent link")
### Classes[¶](#classes "Permanent link")
* [AssistantsClient](#classesassistantsclientmd)
* [Client](#classesclientmd)
* [CronsClient](#classescronsclientmd)
* [RunsClient](#classesrunsclientmd)
* [StoreClient](#classesstoreclientmd)
* [ThreadsClient](#classesthreadsclientmd)
### Interfaces[¶](#interfaces "Permanent link")
* [ClientConfig](#interfacesclientconfigmd)
### Functions[¶](#functions "Permanent link")
* [getApiKey](#functionsgetapikeymd)
**[langchain/langgraph-sdk](https://github.com/langchain/langgraph-sdk "GitHub Repository: langchain/langgraph-sdk")**
---
## [langchain/langgraph-sdk](https://github.com/langchain/langgraph-sdk "GitHub Repository: langchain/langgraph-sdk")/auth[¶](#langchainlanggraph-sdkauth "Permanent link")
### Classes[¶](#classes_1 "Permanent link")
* [Auth](#authclassesauthmd)
* [HTTPException](#authclasseshttpexceptionmd)
### Interfaces[¶](#interfaces_1 "Permanent link")
* [AuthEventValueMap](#authinterfacesautheventvaluemapmd)
### Type Aliases[¶](#type-aliases "Permanent link")
* [AuthFilters](#authtype-aliasesauthfiltersmd)
[**@langchain/langgraph-sdk**](#authreadmemd)
---
[@langchain/langgraph-sdk](#authreadmemd) / Auth
## Class: Auth\<TExtra, TAuthReturn, TUser>[¶](#class-authtextra-tauthreturn-tuser "Permanent link")
Defined in: [src/auth/index.ts:11](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/index.ts#L11)
### Type Parameters[¶](#type-parameters "Permanent link")
• **TExtra** = {}
• **TAuthReturn** *extends* `BaseAuthReturn` = `BaseAuthReturn`
• **TUser** *extends* `BaseUser` = `ToUserLike`\<`TAuthReturn`>
### Constructors[¶](#constructors "Permanent link")
#### new Auth()[¶](#new-auth "Permanent link")
> **new Auth**\<`TExtra`, `TAuthReturn`, `TUser`>(): [`Auth`](#authclassesauthmd)\<`TExtra`, `TAuthReturn`, `TUser`>
##### Returns[¶](#returns "Permanent link")
[`Auth`](#authclassesauthmd)\<`TExtra`, `TAuthReturn`, `TUser`>
### Methods[¶](#methods "Permanent link")
#### authenticate()[¶](#authenticate "Permanent link")
> **authenticate**\<`T`>(`cb`): [`Auth`](#authclassesauthmd)\<`TExtra`, `T`>
Defined in: [src/auth/index.ts:25](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/index.ts#L25)
##### Type Parameters[¶](#type-parameters_1 "Permanent link")
• **T** *extends* `BaseAuthReturn`
##### Parameters[¶](#parameters "Permanent link")
###### cb[¶](#cb "Permanent link")
`AuthenticateCallback`\<`T`>
##### Returns[¶](#returns_1 "Permanent link")
[`Auth`](#authclassesauthmd)\<`TExtra`, `T`>
---
#### on()[¶](#on "Permanent link")
> **on**\<`T`>(`event`, `callback`): `this`
Defined in: [src/auth/index.ts:32](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/index.ts#L32)
##### Type Parameters[¶](#type-parameters_2 "Permanent link")
• **T** *extends* `CallbackEvent`
##### Parameters[¶](#parameters_1 "Permanent link")
###### event[¶](#event "Permanent link")
`T`
###### callback[¶](#callback "Permanent link")
`OnCallback`\<`T`, `TUser`>
##### Returns[¶](#returns_2 "Permanent link")
`this`
[**@langchain/langgraph-sdk**](#authreadmemd)
---
[@langchain/langgraph-sdk](#authreadmemd) / HTTPException
## Class: HTTPException[¶](#class-httpexception "Permanent link")
Defined in: [src/auth/error.ts:66](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/error.ts#L66)
### Extends[¶](#extends "Permanent link")
* `Error`
### Constructors[¶](#constructors_1 "Permanent link")
#### new HTTPException()[¶](#new-httpexception "Permanent link")
> **new HTTPException**(`status`, `options`?): [`HTTPException`](#authclasseshttpexceptionmd)
Defined in: [src/auth/error.ts:70](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/error.ts#L70)
##### Parameters[¶](#parameters_2 "Permanent link")
###### status[¶](#status "Permanent link")
`number`
###### options?[¶](#options "Permanent link")
###### # cause?[¶](#cause "Permanent link")
`unknown`
###### # headers?[¶](#headers "Permanent link")
`HeadersInit`
###### # message?[¶](#message "Permanent link")
`string`
##### Returns[¶](#returns_3 "Permanent link")
[`HTTPException`](#authclasseshttpexceptionmd)
##### Overrides[¶](#overrides "Permanent link")
`Error.constructor`
### Properties[¶](#properties "Permanent link")
#### cause?[¶](#cause_1 "Permanent link")
> `optional` **cause**: `unknown`
Defined in: node\_modules/typescript/lib/lib.es2022.error.d.ts:24
##### Inherited from[¶](#inherited-from "Permanent link")
`Error.cause`
---
#### headers[¶](#headers_1 "Permanent link")
> **headers**: `HeadersInit`
Defined in: [src/auth/error.ts:68](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/error.ts#L68)
---
#### message[¶](#message_1 "Permanent link")
> **message**: `string`
Defined in: node\_modules/typescript/lib/lib.es5.d.ts:1077
##### Inherited from[¶](#inherited-from_1 "Permanent link")
`Error.message`
---
#### name[¶](#name "Permanent link")
> **name**: `string`
Defined in: node\_modules/typescript/lib/lib.es5.d.ts:1076
##### Inherited from[¶](#inherited-from_2 "Permanent link")
`Error.name`
---
#### stack?[¶](#stack "Permanent link")
> `optional` **stack**: `string`
Defined in: node\_modules/typescript/lib/lib.es5.d.ts:1078
##### Inherited from[¶](#inherited-from_3 "Permanent link")
`Error.stack`
---
#### status[¶](#status_1 "Permanent link")
> **status**: `number`
Defined in: [src/auth/error.ts:67](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/error.ts#L67)
---
#### prepareStackTrace()?[¶](#preparestacktrace "Permanent link")
> `static` `optional` **prepareStackTrace**: (`err`, `stackTraces`) => `any`
Defined in: node\_modules/[types/node](https://github.com/types/node "GitHub Repository: types/node")/globals.d.ts:28
Optional override for formatting stack traces
##### Parameters[¶](#parameters_3 "Permanent link")
###### err[¶](#err "Permanent link")
`Error`
###### stackTraces[¶](#stacktraces "Permanent link")
`CallSite`[]
##### Returns[¶](#returns_4 "Permanent link")
`any`
##### See[¶](#see "Permanent link")
<https://v8.dev/docs/stack-trace-api#customizing-stack-traces>
##### Inherited from[¶](#inherited-from_4 "Permanent link")
`Error.prepareStackTrace`
---
#### stackTraceLimit[¶](#stacktracelimit "Permanent link")
> `static` **stackTraceLimit**: `number`
Defined in: node\_modules/[types/node](https://github.com/types/node "GitHub Repository: types/node")/globals.d.ts:30
##### Inherited from[¶](#inherited-from_5 "Permanent link")
`Error.stackTraceLimit`
### Methods[¶](#methods_1 "Permanent link")
#### captureStackTrace()[¶](#capturestacktrace "Permanent link")
> `static` **captureStackTrace**(`targetObject`, `constructorOpt`?): `void`
Defined in: node\_modules/[types/node](https://github.com/types/node "GitHub Repository: types/node")/globals.d.ts:21
Create .stack property on a target object
##### Parameters[¶](#parameters_4 "Permanent link")
###### targetObject[¶](#targetobject "Permanent link")
`object`
###### constructorOpt?[¶](#constructoropt "Permanent link")
`Function`
##### Returns[¶](#returns_5 "Permanent link")
`void`
##### Inherited from[¶](#inherited-from_6 "Permanent link")
`Error.captureStackTrace`
[**@langchain/langgraph-sdk**](#authreadmemd)
---
[@langchain/langgraph-sdk](#authreadmemd) / AuthEventValueMap
## Interface: AuthEventValueMap[¶](#interface-autheventvaluemap "Permanent link")
Defined in: [src/auth/types.ts:218](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L218)
### Properties[¶](#properties_1 "Permanent link")
#### assistants:create[¶](#assistantscreate "Permanent link")
> **assistants:create**: `object`
Defined in: [src/auth/types.ts:226](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L226)
##### assistant\_id?[¶](#assistant_id "Permanent link")
> `optional` **assistant\_id**: `Maybe`\<`string`>
##### config?[¶](#config "Permanent link")
> `optional` **config**: `Maybe`\<`AssistantConfig`>
##### graph\_id[¶](#graph_id "Permanent link")
> **graph\_id**: `string`
##### if\_exists?[¶](#if_exists "Permanent link")
> `optional` **if\_exists**: `Maybe`\<`"raise"` | `"do_nothing"`>
##### metadata?[¶](#metadata "Permanent link")
> `optional` **metadata**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### name?[¶](#name_1 "Permanent link")
> `optional` **name**: `Maybe`\<`string`>
---
#### assistants:delete[¶](#assistantsdelete "Permanent link")
> **assistants:delete**: `object`
Defined in: [src/auth/types.ts:229](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L229)
##### assistant\_id[¶](#assistant_id_1 "Permanent link")
> **assistant\_id**: `string`
---
#### assistants:read[¶](#assistantsread "Permanent link")
> **assistants:read**: `object`
Defined in: [src/auth/types.ts:227](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L227)
##### assistant\_id[¶](#assistant_id_2 "Permanent link")
> **assistant\_id**: `string`
##### metadata?[¶](#metadata_1 "Permanent link")
> `optional` **metadata**: `Maybe`\<`Record`\<`string`, `unknown`>>
---
#### assistants:search[¶](#assistantssearch "Permanent link")
> **assistants:search**: `object`
Defined in: [src/auth/types.ts:230](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L230)
##### graph\_id?[¶](#graph_id_1 "Permanent link")
> `optional` **graph\_id**: `Maybe`\<`string`>
##### limit?[¶](#limit "Permanent link")
> `optional` **limit**: `Maybe`\<`number`>
##### metadata?[¶](#metadata_2 "Permanent link")
> `optional` **metadata**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### offset?[¶](#offset "Permanent link")
> `optional` **offset**: `Maybe`\<`number`>
---
#### assistants:update[¶](#assistantsupdate "Permanent link")
> **assistants:update**: `object`
Defined in: [src/auth/types.ts:228](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L228)
##### assistant\_id[¶](#assistant_id_3 "Permanent link")
> **assistant\_id**: `string`
##### config?[¶](#config_1 "Permanent link")
> `optional` **config**: `Maybe`\<`AssistantConfig`>
##### graph\_id?[¶](#graph_id_2 "Permanent link")
> `optional` **graph\_id**: `Maybe`\<`string`>
##### metadata?[¶](#metadata_3 "Permanent link")
> `optional` **metadata**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### name?[¶](#name_2 "Permanent link")
> `optional` **name**: `Maybe`\<`string`>
##### version?[¶](#version "Permanent link")
> `optional` **version**: `Maybe`\<`number`>
---
#### crons:create[¶](#cronscreate "Permanent link")
> **crons:create**: `object`
Defined in: [src/auth/types.ts:232](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L232)
##### cron\_id?[¶](#cron_id "Permanent link")
> `optional` **cron\_id**: `Maybe`\<`string`>
##### end\_time?[¶](#end_time "Permanent link")
> `optional` **end\_time**: `Maybe`\<`string`>
##### payload?[¶](#payload "Permanent link")
> `optional` **payload**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### schedule[¶](#schedule "Permanent link")
> **schedule**: `string`
##### thread\_id?[¶](#thread_id "Permanent link")
> `optional` **thread\_id**: `Maybe`\<`string`>
##### user\_id?[¶](#user_id "Permanent link")
> `optional` **user\_id**: `Maybe`\<`string`>
---
#### crons:delete[¶](#cronsdelete "Permanent link")
> **crons:delete**: `object`
Defined in: [src/auth/types.ts:235](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L235)
##### cron\_id[¶](#cron_id_1 "Permanent link")
> **cron\_id**: `string`
---
#### crons:read[¶](#cronsread "Permanent link")
> **crons:read**: `object`
Defined in: [src/auth/types.ts:233](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L233)
##### cron\_id[¶](#cron_id_2 "Permanent link")
> **cron\_id**: `string`
---
#### crons:search[¶](#cronssearch "Permanent link")
> **crons:search**: `object`
Defined in: [src/auth/types.ts:236](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L236)
##### assistant\_id?[¶](#assistant_id_4 "Permanent link")
> `optional` **assistant\_id**: `Maybe`\<`string`>
##### limit?[¶](#limit_1 "Permanent link")
> `optional` **limit**: `Maybe`\<`number`>
##### offset?[¶](#offset_1 "Permanent link")
> `optional` **offset**: `Maybe`\<`number`>
##### thread\_id?[¶](#thread_id_1 "Permanent link")
> `optional` **thread\_id**: `Maybe`\<`string`>
---
#### crons:update[¶](#cronsupdate "Permanent link")
> **crons:update**: `object`
Defined in: [src/auth/types.ts:234](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L234)
##### cron\_id[¶](#cron_id_3 "Permanent link")
> **cron\_id**: `string`
##### payload?[¶](#payload_1 "Permanent link")
> `optional` **payload**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### schedule?[¶](#schedule_1 "Permanent link")
> `optional` **schedule**: `Maybe`\<`string`>
---
#### store:delete[¶](#storedelete "Permanent link")
> **store:delete**: `object`
Defined in: [src/auth/types.ts:242](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L242)
##### key[¶](#key "Permanent link")
> **key**: `string`
##### namespace?[¶](#namespace "Permanent link")
> `optional` **namespace**: `Maybe`\<`string`[]>
---
#### store:get[¶](#storeget "Permanent link")
> **store:get**: `object`
Defined in: [src/auth/types.ts:239](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L239)
##### key[¶](#key_1 "Permanent link")
> **key**: `string`
##### namespace[¶](#namespace_1 "Permanent link")
> **namespace**: `Maybe`\<`string`[]>
---
#### store:list\_namespaces[¶](#storelist_namespaces "Permanent link")
> **store:list\_namespaces**: `object`
Defined in: [src/auth/types.ts:241](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L241)
##### limit?[¶](#limit_2 "Permanent link")
> `optional` **limit**: `Maybe`\<`number`>
##### max\_depth?[¶](#max_depth "Permanent link")
> `optional` **max\_depth**: `Maybe`\<`number`>
##### namespace?[¶](#namespace_2 "Permanent link")
> `optional` **namespace**: `Maybe`\<`string`[]>
##### offset?[¶](#offset_2 "Permanent link")
> `optional` **offset**: `Maybe`\<`number`>
##### suffix?[¶](#suffix "Permanent link")
> `optional` **suffix**: `Maybe`\<`string`[]>
---
#### store:put[¶](#storeput "Permanent link")
> **store:put**: `object`
Defined in: [src/auth/types.ts:238](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L238)
##### key[¶](#key_2 "Permanent link")
> **key**: `string`
##### namespace[¶](#namespace_3 "Permanent link")
> **namespace**: `string`[]
##### value[¶](#value "Permanent link")
> **value**: `Record`\<`string`, `unknown`>
---
#### store:search[¶](#storesearch "Permanent link")
> **store:search**: `object`
Defined in: [src/auth/types.ts:240](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L240)
##### filter?[¶](#filter "Permanent link")
> `optional` **filter**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### limit?[¶](#limit_3 "Permanent link")
> `optional` **limit**: `Maybe`\<`number`>
##### namespace?[¶](#namespace_4 "Permanent link")
> `optional` **namespace**: `Maybe`\<`string`[]>
##### offset?[¶](#offset_3 "Permanent link")
> `optional` **offset**: `Maybe`\<`number`>
##### query?[¶](#query "Permanent link")
> `optional` **query**: `Maybe`\<`string`>
---
#### threads:create[¶](#threadscreate "Permanent link")
> **threads:create**: `object`
Defined in: [src/auth/types.ts:219](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L219)
##### if\_exists?[¶](#if_exists_1 "Permanent link")
> `optional` **if\_exists**: `Maybe`\<`"raise"` | `"do_nothing"`>
##### metadata?[¶](#metadata_4 "Permanent link")
> `optional` **metadata**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### thread\_id?[¶](#thread_id_2 "Permanent link")
> `optional` **thread\_id**: `Maybe`\<`string`>
---
#### threads:create\_run[¶](#threadscreate_run "Permanent link")
> **threads:create\_run**: `object`
Defined in: [src/auth/types.ts:224](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L224)
##### after\_seconds?[¶](#after_seconds "Permanent link")
> `optional` **after\_seconds**: `Maybe`\<`number`>
##### assistant\_id[¶](#assistant_id_5 "Permanent link")
> **assistant\_id**: `string`
##### if\_not\_exists?[¶](#if_not_exists "Permanent link")
> `optional` **if\_not\_exists**: `Maybe`\<`"reject"` | `"create"`>
##### kwargs[¶](#kwargs "Permanent link")
> **kwargs**: `Record`\<`string`, `unknown`>
##### metadata?[¶](#metadata_5 "Permanent link")
> `optional` **metadata**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### multitask\_strategy?[¶](#multitask_strategy "Permanent link")
> `optional` **multitask\_strategy**: `Maybe`\<`"reject"` | `"interrupt"` | `"rollback"` | `"enqueue"`>
##### prevent\_insert\_if\_inflight?[¶](#prevent_insert_if_inflight "Permanent link")
> `optional` **prevent\_insert\_if\_inflight**: `Maybe`\<`boolean`>
##### run\_id[¶](#run_id "Permanent link")
> **run\_id**: `string`
##### status[¶](#status_2 "Permanent link")
> **status**: `Maybe`\<`"pending"` | `"running"` | `"error"` | `"success"` | `"timeout"` | `"interrupted"`>
##### thread\_id?[¶](#thread_id_3 "Permanent link")
> `optional` **thread\_id**: `Maybe`\<`string`>
---
#### threads:delete[¶](#threadsdelete "Permanent link")
> **threads:delete**: `object`
Defined in: [src/auth/types.ts:222](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L222)
##### run\_id?[¶](#run_id_1 "Permanent link")
> `optional` **run\_id**: `Maybe`\<`string`>
##### thread\_id?[¶](#thread_id_4 "Permanent link")
> `optional` **thread\_id**: `Maybe`\<`string`>
---
#### threads:read[¶](#threadsread "Permanent link")
> **threads:read**: `object`
Defined in: [src/auth/types.ts:220](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L220)
##### thread\_id?[¶](#thread_id_5 "Permanent link")
> `optional` **thread\_id**: `Maybe`\<`string`>
---
#### threads:search[¶](#threadssearch "Permanent link")
> **threads:search**: `object`
Defined in: [src/auth/types.ts:223](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L223)
##### limit?[¶](#limit_4 "Permanent link")
> `optional` **limit**: `Maybe`\<`number`>
##### metadata?[¶](#metadata_6 "Permanent link")
> `optional` **metadata**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### offset?[¶](#offset_4 "Permanent link")
> `optional` **offset**: `Maybe`\<`number`>
##### status?[¶](#status_3 "Permanent link")
> `optional` **status**: `Maybe`\<`"error"` | `"interrupted"` | `"idle"` | `"busy"` | `string` & `object`>
##### thread\_id?[¶](#thread_id_6 "Permanent link")
> `optional` **thread\_id**: `Maybe`\<`string`>
##### values?[¶](#values "Permanent link")
> `optional` **values**: `Maybe`\<`Record`\<`string`, `unknown`>>
---
#### threads:update[¶](#threadsupdate "Permanent link")
> **threads:update**: `object`
Defined in: [src/auth/types.ts:221](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L221)
##### action?[¶](#action "Permanent link")
> `optional` **action**: `Maybe`\<`"interrupt"` | `"rollback"`>
##### metadata?[¶](#metadata_7 "Permanent link")
> `optional` **metadata**: `Maybe`\<`Record`\<`string`, `unknown`>>
##### thread\_id?[¶](#thread_id_7 "Permanent link")
> `optional` **thread\_id**: `Maybe`\<`string`>
[**@langchain/langgraph-sdk**](#authreadmemd)
---
[@langchain/langgraph-sdk](#authreadmemd) / AuthFilters
## Type Alias: AuthFilters\<TKey>[¶](#type-alias-authfilterstkey "Permanent link")
> **AuthFilters**\<`TKey`>: { [key in TKey]: string | { [op in "\(contains" \| "\)eq"]?: string } }
Defined in: [src/auth/types.ts:367](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/auth/types.ts#L367)
### Type Parameters[¶](#type-parameters_3 "Permanent link")
• **TKey** *extends* `string` | `number` | `symbol`
[**@langchain/langgraph-sdk**](#readmemd)
---
[@langchain/langgraph-sdk](#readmemd) / AssistantsClient
## Class: AssistantsClient[¶](#class-assistantsclient "Permanent link")
Defined in: [client.ts:294](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L294)
### Extends[¶](#extends_1 "Permanent link")
* `BaseClient`
### Constructors[¶](#constructors_2 "Permanent link")
#### new AssistantsClient()[¶](#new-assistantsclient "Permanent link")
> **new AssistantsClient**(`config`?): [`AssistantsClient`](#classesassistantsclientmd)
Defined in: [client.ts:88](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L88)
##### Parameters[¶](#parameters_5 "Permanent link")
###### config?[¶](#config_2 "Permanent link")
[`ClientConfig`](#interfacesclientconfigmd)
##### Returns[¶](#returns_6 "Permanent link")
[`AssistantsClient`](#classesassistantsclientmd)
##### Inherited from[¶](#inherited-from_7 "Permanent link")
`BaseClient.constructor`
### Methods[¶](#methods_2 "Permanent link")
#### create()[¶](#create "Permanent link")
> **create**(`payload`): `Promise`\<`Assistant`>
Defined in: [client.ts:359](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L359)
Create a new assistant.
##### Parameters[¶](#parameters_6 "Permanent link")
###### payload[¶](#payload_2 "Permanent link")
Payload for creating an assistant.
###### # assistantId?[¶](#assistantid "Permanent link")
`string`
###### # config?[¶](#config_3 "Permanent link")
`Config`
###### # description?[¶](#description "Permanent link")
`string`
###### # graphId[¶](#graphid "Permanent link")
`string`
###### # ifExists?[¶](#ifexists "Permanent link")
`OnConflictBehavior`
###### # metadata?[¶](#metadata_8 "Permanent link")
`Metadata`
###### # name?[¶](#name_3 "Permanent link")
`string`
##### Returns[¶](#returns_7 "Permanent link")
`Promise`\<`Assistant`>
The created assistant.
---
#### delete()[¶](#delete "Permanent link")
> **delete**(`assistantId`): `Promise`\<`void`>
Defined in: [client.ts:415](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L415)
Delete an assistant.
##### Parameters[¶](#parameters_7 "Permanent link")
###### assistantId[¶](#assistantid_1 "Permanent link")
`string`
ID of the assistant.
##### Returns[¶](#returns_8 "Permanent link")
`Promise`\<`void`>
---
#### get()[¶](#get "Permanent link")
> **get**(`assistantId`): `Promise`\<`Assistant`>
Defined in: [client.ts:301](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L301)
Get an assistant by ID.
##### Parameters[¶](#parameters_8 "Permanent link")
###### assistantId[¶](#assistantid_2 "Permanent link")
`string`
The ID of the assistant.
##### Returns[¶](#returns_9 "Permanent link")
`Promise`\<`Assistant`>
Assistant
---
#### getGraph()[¶](#getgraph "Permanent link")
> **getGraph**(`assistantId`, `options`?): `Promise`\<`AssistantGraph`>
Defined in: [client.ts:311](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L311)
Get the JSON representation of the graph assigned to a runnable
##### Parameters[¶](#parameters_9 "Permanent link")
###### assistantId[¶](#assistantid_3 "Permanent link")
`string`
The ID of the assistant.
###### options?[¶](#options_1 "Permanent link")
###### # xray?[¶](#xray "Permanent link")
`number` | `boolean`
Whether to include subgraphs in the serialized graph representation. If an integer value is provided, only subgraphs with a depth less than or equal to the value will be included.
##### Returns[¶](#returns_10 "Permanent link")
`Promise`\<`AssistantGraph`>
Serialized graph
---
#### getSchemas()[¶](#getschemas "Permanent link")
> **getSchemas**(`assistantId`): `Promise`\<`GraphSchema`>
Defined in: [client.ts:325](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L325)
Get the state and config schema of the graph assigned to a runnable
##### Parameters[¶](#parameters_10 "Permanent link")
###### assistantId[¶](#assistantid_4 "Permanent link")
`string`
The ID of the assistant.
##### Returns[¶](#returns_11 "Permanent link")
`Promise`\<`GraphSchema`>
Graph schema
---
#### getSubgraphs()[¶](#getsubgraphs "Permanent link")
> **getSubgraphs**(`assistantId`, `options`?): `Promise`\<`Subgraphs`>
Defined in: [client.ts:336](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L336)
Get the schemas of an assistant by ID.
##### Parameters[¶](#parameters_11 "Permanent link")
###### assistantId[¶](#assistantid_5 "Permanent link")
`string`
The ID of the assistant to get the schema of.
###### options?[¶](#options_2 "Permanent link")
Additional options for getting subgraphs, such as namespace or recursion extraction.
###### # namespace?[¶](#namespace_5 "Permanent link")
`string`
###### # recurse?[¶](#recurse "Permanent link")
`boolean`
##### Returns[¶](#returns_12 "Permanent link")
`Promise`\<`Subgraphs`>
The subgraphs of the assistant.
---
#### getVersions()[¶](#getversions "Permanent link")
> **getVersions**(`assistantId`, `payload`?): `Promise`\<`AssistantVersion`[]>
Defined in: [client.ts:453](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L453)
List all versions of an assistant.
##### Parameters[¶](#parameters_12 "Permanent link")
###### assistantId[¶](#assistantid_6 "Permanent link")
`string`
ID of the assistant.
###### payload?[¶](#payload_3 "Permanent link")
###### # limit?[¶](#limit_5 "Permanent link")
`number`
###### # metadata?[¶](#metadata_9 "Permanent link")
`Metadata`
###### # offset?[¶](#offset_5 "Permanent link")
`number`
##### Returns[¶](#returns_13 "Permanent link")
`Promise`\<`AssistantVersion`[]>
List of assistant versions.
---
#### search()[¶](#search "Permanent link")
> **search**(`query`?): `Promise`\<`Assistant`[]>
Defined in: [client.ts:426](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L426)
List assistants.
##### Parameters[¶](#parameters_13 "Permanent link")
###### query?[¶](#query_1 "Permanent link")
Query options.
###### # graphId?[¶](#graphid_1 "Permanent link")
`string`
###### # limit?[¶](#limit_6 "Permanent link")
`number`
###### # metadata?[¶](#metadata_10 "Permanent link")
`Metadata`
###### # offset?[¶](#offset_6 "Permanent link")
`number`
###### # sortBy?[¶](#sortby "Permanent link")
`AssistantSortBy`
###### # sortOrder?[¶](#sortorder "Permanent link")
`SortOrder`
##### Returns[¶](#returns_14 "Permanent link")
`Promise`\<`Assistant`[]>
List of assistants.
---
#### setLatest()[¶](#setlatest "Permanent link")
> **setLatest**(`assistantId`, `version`): `Promise`\<`Assistant`>
Defined in: [client.ts:481](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L481)
Change the version of an assistant.
##### Parameters[¶](#parameters_14 "Permanent link")
###### assistantId[¶](#assistantid_7 "Permanent link")
`string`
ID of the assistant.
###### version[¶](#version_1 "Permanent link")
`number`
The version to change to.
##### Returns[¶](#returns_15 "Permanent link")
`Promise`\<`Assistant`>
The updated assistant.
---
#### update()[¶](#update "Permanent link")
> **update**(`assistantId`, `payload`): `Promise`\<`Assistant`>
Defined in: [client.ts:388](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L388)
Update an assistant.
##### Parameters[¶](#parameters_15 "Permanent link")
###### assistantId[¶](#assistantid_8 "Permanent link")
`string`
ID of the assistant.
###### payload[¶](#payload_4 "Permanent link")
Payload for updating the assistant.
###### # config?[¶](#config_4 "Permanent link")
`Config`
###### # description?[¶](#description_1 "Permanent link")
`string`
###### # graphId?[¶](#graphid_2 "Permanent link")
`string`
###### # metadata?[¶](#metadata_11 "Permanent link")
`Metadata`
###### # name?[¶](#name_4 "Permanent link")
`string`
##### Returns[¶](#returns_16 "Permanent link")
`Promise`\<`Assistant`>
The updated assistant.
[**@langchain/langgraph-sdk**](#readmemd)
---
[@langchain/langgraph-sdk](#readmemd) / Client
## Class: Client\<TStateType, TUpdateType, TCustomEventType>[¶](#class-clienttstatetype-tupdatetype-tcustomeventtype "Permanent link")
Defined in: [client.ts:1448](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1448)
### Type Parameters[¶](#type-parameters_4 "Permanent link")
• **TStateType** = `DefaultValues`
• **TUpdateType** = `TStateType`
• **TCustomEventType** = `unknown`
### Constructors[¶](#constructors_3 "Permanent link")
#### new Client()[¶](#new-client "Permanent link")
> **new Client**\<`TStateType`, `TUpdateType`, `TCustomEventType`>(`config`?): [`Client`](#classesclientmd)\<`TStateType`, `TUpdateType`, `TCustomEventType`>
Defined in: [client.ts:1484](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1484)
##### Parameters[¶](#parameters_16 "Permanent link")
###### config?[¶](#config_5 "Permanent link")
[`ClientConfig`](#interfacesclientconfigmd)
##### Returns[¶](#returns_17 "Permanent link")
[`Client`](#classesclientmd)\<`TStateType`, `TUpdateType`, `TCustomEventType`>
### Properties[¶](#properties_2 "Permanent link")
#### ~ui[¶](#ui "Permanent link")
> **~ui**: `UiClient`
Defined in: [client.ts:1482](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1482)
**`Internal`**
The client for interacting with the UI.
Used by LoadExternalComponent and the API might change in the future.
---
#### assistants[¶](#assistants "Permanent link")
> **assistants**: [`AssistantsClient`](#classesassistantsclientmd)
Defined in: [client.ts:1456](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1456)
The client for interacting with assistants.
---
#### crons[¶](#crons "Permanent link")
> **crons**: [`CronsClient`](#classescronsclientmd)
Defined in: [client.ts:1471](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1471)
The client for interacting with cron runs.
---
#### runs[¶](#runs "Permanent link")
> **runs**: [`RunsClient`](#classesrunsclientmd)\<`TStateType`, `TUpdateType`, `TCustomEventType`>
Defined in: [client.ts:1466](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1466)
The client for interacting with runs.
---
#### store[¶](#store "Permanent link")
> **store**: [`StoreClient`](#classesstoreclientmd)
Defined in: [client.ts:1476](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1476)
The client for interacting with the KV store.
---
#### threads[¶](#threads "Permanent link")
> **threads**: [`ThreadsClient`](#classesthreadsclientmd)\<`TStateType`, `TUpdateType`>
Defined in: [client.ts:1461](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1461)
The client for interacting with threads.
[**@langchain/langgraph-sdk**](#readmemd)
---
[@langchain/langgraph-sdk](#readmemd) / CronsClient
## Class: CronsClient[¶](#class-cronsclient "Permanent link")
Defined in: [client.ts:197](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L197)
### Extends[¶](#extends_2 "Permanent link")
* `BaseClient`
### Constructors[¶](#constructors_4 "Permanent link")
#### new CronsClient()[¶](#new-cronsclient "Permanent link")
> **new CronsClient**(`config`?): [`CronsClient`](#classescronsclientmd)
Defined in: [client.ts:88](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L88)
##### Parameters[¶](#parameters_17 "Permanent link")
###### config?[¶](#config_6 "Permanent link")
[`ClientConfig`](#interfacesclientconfigmd)
##### Returns[¶](#returns_18 "Permanent link")
[`CronsClient`](#classescronsclientmd)
##### Inherited from[¶](#inherited-from_8 "Permanent link")
`BaseClient.constructor`
### Methods[¶](#methods_3 "Permanent link")
#### create()[¶](#create_1 "Permanent link")
> **create**(`assistantId`, `payload`?): `Promise`\<`CronCreateResponse`>
Defined in: [client.ts:238](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L238)
##### Parameters[¶](#parameters_18 "Permanent link")
###### assistantId[¶](#assistantid_9 "Permanent link")
`string`
Assistant ID to use for this cron job.
###### payload?[¶](#payload_5 "Permanent link")
`CronsCreatePayload`
Payload for creating a cron job.
##### Returns[¶](#returns_19 "Permanent link")
`Promise`\<`CronCreateResponse`>
---
#### createForThread()[¶](#createforthread "Permanent link")
> **createForThread**(`threadId`, `assistantId`, `payload`?): `Promise`\<`CronCreateForThreadResponse`>
Defined in: [client.ts:205](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L205)
##### Parameters[¶](#parameters_19 "Permanent link")
###### threadId[¶](#threadid "Permanent link")
`string`
The ID of the thread.
###### assistantId[¶](#assistantid_10 "Permanent link")
`string`
Assistant ID to use for this cron job.
###### payload?[¶](#payload_6 "Permanent link")
`CronsCreatePayload`
Payload for creating a cron job.
##### Returns[¶](#returns_20 "Permanent link")
`Promise`\<`CronCreateForThreadResponse`>
The created background run.
---
#### delete()[¶](#delete_1 "Permanent link")
> **delete**(`cronId`): `Promise`\<`void`>
Defined in: [client.ts:265](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L265)
##### Parameters[¶](#parameters_20 "Permanent link")
###### cronId[¶](#cronid "Permanent link")
`string`
Cron ID of Cron job to delete.
##### Returns[¶](#returns_21 "Permanent link")
`Promise`\<`void`>
---
#### search()[¶](#search_1 "Permanent link")
> **search**(`query`?): `Promise`\<`Cron`[]>
Defined in: [client.ts:276](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L276)
##### Parameters[¶](#parameters_21 "Permanent link")
###### query?[¶](#query_2 "Permanent link")
Query options.
###### # assistantId?[¶](#assistantid_11 "Permanent link")
`string`
###### # limit?[¶](#limit_7 "Permanent link")
`number`
###### # offset?[¶](#offset_7 "Permanent link")
`number`
###### # threadId?[¶](#threadid_1 "Permanent link")
`string`
##### Returns[¶](#returns_22 "Permanent link")
`Promise`\<`Cron`[]>
List of crons.
[**@langchain/langgraph-sdk**](#readmemd)
---
[@langchain/langgraph-sdk](#readmemd) / RunsClient
## Class: RunsClient\<TStateType, TUpdateType, TCustomEventType>[¶](#class-runsclienttstatetype-tupdatetype-tcustomeventtype "Permanent link")
Defined in: [client.ts:776](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L776)
### Extends[¶](#extends_3 "Permanent link")
* `BaseClient`
### Type Parameters[¶](#type-parameters_5 "Permanent link")
• **TStateType** = `DefaultValues`
• **TUpdateType** = `TStateType`
• **TCustomEventType** = `unknown`
### Constructors[¶](#constructors_5 "Permanent link")
#### new RunsClient()[¶](#new-runsclient "Permanent link")
> **new RunsClient**\<`TStateType`, `TUpdateType`, `TCustomEventType`>(`config`?): [`RunsClient`](#classesrunsclientmd)\<`TStateType`, `TUpdateType`, `TCustomEventType`>
Defined in: [client.ts:88](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L88)
##### Parameters[¶](#parameters_22 "Permanent link")
###### config?[¶](#config_7 "Permanent link")
[`ClientConfig`](#interfacesclientconfigmd)
##### Returns[¶](#returns_23 "Permanent link")
[`RunsClient`](#classesrunsclientmd)\<`TStateType`, `TUpdateType`, `TCustomEventType`>
##### Inherited from[¶](#inherited-from_9 "Permanent link")
`BaseClient.constructor`
### Methods[¶](#methods_4 "Permanent link")
#### cancel()[¶](#cancel "Permanent link")
> **cancel**(`threadId`, `runId`, `wait`, `action`): `Promise`\<`void`>
Defined in: [client.ts:1063](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1063)
Cancel a run.
##### Parameters[¶](#parameters_23 "Permanent link")
###### threadId[¶](#threadid_2 "Permanent link")
`string`
The ID of the thread.
###### runId[¶](#runid "Permanent link")
`string`
The ID of the run.
###### wait[¶](#wait "Permanent link")
`boolean` = `false`
Whether to block when canceling
###### action[¶](#action_1 "Permanent link")
`CancelAction` = `"interrupt"`
Action to take when cancelling the run. Possible values are `interrupt` or `rollback`. Default is `interrupt`.
##### Returns[¶](#returns_24 "Permanent link")
`Promise`\<`void`>
---
#### create()[¶](#create_2 "Permanent link")
> **create**(`threadId`, `assistantId`, `payload`?): `Promise`\<`Run`>
Defined in: [client.ts:885](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L885)
Create a run.
##### Parameters[¶](#parameters_24 "Permanent link")
###### threadId[¶](#threadid_3 "Permanent link")
`string`
The ID of the thread.
###### assistantId[¶](#assistantid_12 "Permanent link")
`string`
Assistant ID to use for this run.
###### payload?[¶](#payload_7 "Permanent link")
`RunsCreatePayload`
Payload for creating a run.
##### Returns[¶](#returns_25 "Permanent link")
`Promise`\<`Run`>
The created run.
---
#### createBatch()[¶](#createbatch "Permanent link")
> **createBatch**(`payloads`): `Promise`\<`Run`[]>
Defined in: [client.ts:921](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L921)
Create a batch of stateless background runs.
##### Parameters[¶](#parameters_25 "Permanent link")
###### payloads[¶](#payloads "Permanent link")
`RunsCreatePayload` & `object`[]
An array of payloads for creating runs.
##### Returns[¶](#returns_26 "Permanent link")
`Promise`\<`Run`[]>
An array of created runs.
---
#### delete()[¶](#delete_2 "Permanent link")
> **delete**(`threadId`, `runId`): `Promise`\<`void`>
Defined in: [client.ts:1157](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1157)
Delete a run.
##### Parameters[¶](#parameters_26 "Permanent link")
###### threadId[¶](#threadid_4 "Permanent link")
`string`
The ID of the thread.
###### runId[¶](#runid_1 "Permanent link")
`string`
The ID of the run.
##### Returns[¶](#returns_27 "Permanent link")
`Promise`\<`void`>
---
#### get()[¶](#get_1 "Permanent link")
> **get**(`threadId`, `runId`): `Promise`\<`Run`>
Defined in: [client.ts:1050](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1050)
Get a run by ID.
##### Parameters[¶](#parameters_27 "Permanent link")
###### threadId[¶](#threadid_5 "Permanent link")
`string`
The ID of the thread.
###### runId[¶](#runid_2 "Permanent link")
`string`
The ID of the run.
##### Returns[¶](#returns_28 "Permanent link")
`Promise`\<`Run`>
The run.
---
#### join()[¶](#join "Permanent link")
> **join**(`threadId`, `runId`, `options`?): `Promise`\<`void`>
Defined in: [client.ts:1085](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1085)
Block until a run is done.
##### Parameters[¶](#parameters_28 "Permanent link")
###### threadId[¶](#threadid_6 "Permanent link")
`string`
The ID of the thread.
###### runId[¶](#runid_3 "Permanent link")
`string`
The ID of the run.
###### options?[¶](#options_3 "Permanent link")
###### # signal?[¶](#signal "Permanent link")
`AbortSignal`
##### Returns[¶](#returns_29 "Permanent link")
`Promise`\<`void`>
---
#### joinStream()[¶](#joinstream "Permanent link")
> **joinStream**(`threadId`, `runId`, `options`?): `AsyncGenerator`\<{ `data`: `any`; `event`: `StreamEvent`; }>
Defined in: [client.ts:1111](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1111)
Stream output from a run in real-time, until the run is done.
Output is not buffered, so any output produced before this call will
not be received here.
##### Parameters[¶](#parameters_29 "Permanent link")
###### threadId[¶](#threadid_7 "Permanent link")
`string`
The ID of the thread.
###### runId[¶](#runid_4 "Permanent link")
`string`
The ID of the run.
###### options?[¶](#options_4 "Permanent link")
Additional options for controlling the stream behavior:
- signal: An AbortSignal that can be used to cancel the stream request
- cancelOnDisconnect: When true, automatically cancels the run if the client disconnects from the stream
- streamMode: Controls what types of events to receive from the stream (can be a single mode or array of modes)
Must be a subset of the stream modes passed when creating the run. Background runs default to having the union of all
stream modes enabled.
`AbortSignal` | { `cancelOnDisconnect`: `boolean`; `signal`: `AbortSignal`; `streamMode`: `StreamMode` | `StreamMode`[]; }
##### Returns[¶](#returns_30 "Permanent link")
`AsyncGenerator`\<{ `data`: `any`; `event`: `StreamEvent`; }>
An async generator yielding stream parts.
---
#### list()[¶](#list "Permanent link")
> **list**(`threadId`, `options`?): `Promise`\<`Run`[]>
Defined in: [client.ts:1013](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1013)
List all runs for a thread.
##### Parameters[¶](#parameters_30 "Permanent link")
###### threadId[¶](#threadid_8 "Permanent link")
`string`
The ID of the thread.
###### options?[¶](#options_5 "Permanent link")
Filtering and pagination options.
###### # limit?[¶](#limit_8 "Permanent link")
`number`
Maximum number of runs to return.
Defaults to 10
###### # offset?[¶](#offset_8 "Permanent link")
`number`
Offset to start from.
Defaults to 0.
###### # status?[¶](#status_4 "Permanent link")
`RunStatus`
Status of the run to filter by.
##### Returns[¶](#returns_31 "Permanent link")
`Promise`\<`Run`[]>
List of runs.
---
#### stream()[¶](#stream "Permanent link")
Create a run and stream the results.
##### Param[¶](#param "Permanent link")
The ID of the thread.
##### Param[¶](#param_1 "Permanent link")
Assistant ID to use for this run.
##### Param[¶](#param_2 "Permanent link")
Payload for creating a run.
##### Call Signature[¶](#call-signature "Permanent link")
> **stream**\<`TStreamMode`, `TSubgraphs`>(`threadId`, `assistantId`, `payload`?): `TypedAsyncGenerator`\<`TStreamMode`, `TSubgraphs`, `TStateType`, `TUpdateType`, `TCustomEventType`>
Defined in: [client.ts:781](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L781)
###### Type Parameters[¶](#type-parameters_6 "Permanent link")
• **TStreamMode** *extends* `StreamMode` | `StreamMode`[] = `StreamMode`
• **TSubgraphs** *extends* `boolean` = `false`
###### Parameters[¶](#parameters_31 "Permanent link")
###### # threadId[¶](#threadid_9 "Permanent link")
`null`
###### # assistantId[¶](#assistantid_13 "Permanent link")
`string`
###### # payload?[¶](#payload_8 "Permanent link")
`Omit`\<`RunsStreamPayload`\<`TStreamMode`, `TSubgraphs`>, `"multitaskStrategy"` | `"onCompletion"`>
###### Returns[¶](#returns_32 "Permanent link")
`TypedAsyncGenerator`\<`TStreamMode`, `TSubgraphs`, `TStateType`, `TUpdateType`, `TCustomEventType`>
##### Call Signature[¶](#call-signature_1 "Permanent link")
> **stream**\<`TStreamMode`, `TSubgraphs`>(`threadId`, `assistantId`, `payload`?): `TypedAsyncGenerator`\<`TStreamMode`, `TSubgraphs`, `TStateType`, `TUpdateType`, `TCustomEventType`>
Defined in: [client.ts:799](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L799)
###### Type Parameters[¶](#type-parameters_7 "Permanent link")
• **TStreamMode** *extends* `StreamMode` | `StreamMode`[] = `StreamMode`
• **TSubgraphs** *extends* `boolean` = `false`
###### Parameters[¶](#parameters_32 "Permanent link")
###### # threadId[¶](#threadid_10 "Permanent link")
`string`
###### # assistantId[¶](#assistantid_14 "Permanent link")
`string`
###### # payload?[¶](#payload_9 "Permanent link")
`RunsStreamPayload`\<`TStreamMode`, `TSubgraphs`>
###### Returns[¶](#returns_33 "Permanent link")
`TypedAsyncGenerator`\<`TStreamMode`, `TSubgraphs`, `TStateType`, `TUpdateType`, `TCustomEventType`>
---
#### wait()[¶](#wait_1 "Permanent link")
Create a run and wait for it to complete.
##### Param[¶](#param_3 "Permanent link")
The ID of the thread.
##### Param[¶](#param_4 "Permanent link")
Assistant ID to use for this run.
##### Param[¶](#param_5 "Permanent link")
Payload for creating a run.
##### Call Signature[¶](#call-signature_2 "Permanent link")
> **wait**(`threadId`, `assistantId`, `payload`?): `Promise`\<`DefaultValues`>
Defined in: [client.ts:938](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L938)
###### Parameters[¶](#parameters_33 "Permanent link")
###### # threadId[¶](#threadid_11 "Permanent link")
`null`
###### # assistantId[¶](#assistantid_15 "Permanent link")
`string`
###### # payload?[¶](#payload_10 "Permanent link")
`Omit`\<`RunsWaitPayload`, `"multitaskStrategy"` | `"onCompletion"`>
###### Returns[¶](#returns_34 "Permanent link")
`Promise`\<`DefaultValues`>
##### Call Signature[¶](#call-signature_3 "Permanent link")
> **wait**(`threadId`, `assistantId`, `payload`?): `Promise`\<`DefaultValues`>
Defined in: [client.ts:944](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L944)
###### Parameters[¶](#parameters_34 "Permanent link")
###### # threadId[¶](#threadid_12 "Permanent link")
`string`
###### # assistantId[¶](#assistantid_16 "Permanent link")
`string`
###### # payload?[¶](#payload_11 "Permanent link")
`RunsWaitPayload`
###### Returns[¶](#returns_35 "Permanent link")
`Promise`\<`DefaultValues`>
[**@langchain/langgraph-sdk**](#readmemd)
---
[@langchain/langgraph-sdk](#readmemd) / StoreClient
## Class: StoreClient[¶](#class-storeclient "Permanent link")
Defined in: [client.ts:1175](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1175)
### Extends[¶](#extends_4 "Permanent link")
* `BaseClient`
### Constructors[¶](#constructors_6 "Permanent link")
#### new StoreClient()[¶](#new-storeclient "Permanent link")
> **new StoreClient**(`config`?): [`StoreClient`](#classesstoreclientmd)
Defined in: [client.ts:88](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L88)
##### Parameters[¶](#parameters_35 "Permanent link")
###### config?[¶](#config_8 "Permanent link")
[`ClientConfig`](#interfacesclientconfigmd)
##### Returns[¶](#returns_36 "Permanent link")
[`StoreClient`](#classesstoreclientmd)
##### Inherited from[¶](#inherited-from_10 "Permanent link")
`BaseClient.constructor`
### Methods[¶](#methods_5 "Permanent link")
#### deleteItem()[¶](#deleteitem "Permanent link")
> **deleteItem**(`namespace`, `key`): `Promise`\<`void`>
Defined in: [client.ts:1296](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1296)
Delete an item.
##### Parameters[¶](#parameters_36 "Permanent link")
###### namespace[¶](#namespace_6 "Permanent link")
`string`[]
A list of strings representing the namespace path.
###### key[¶](#key_3 "Permanent link")
`string`
The unique identifier for the item.
##### Returns[¶](#returns_37 "Permanent link")
`Promise`\<`void`>
Promise
---
#### getItem()[¶](#getitem "Permanent link")
> **getItem**(`namespace`, `key`, `options`?): `Promise`\<`null` | `Item`>
Defined in: [client.ts:1252](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1252)
Retrieve a single item.
##### Parameters[¶](#parameters_37 "Permanent link")
###### namespace[¶](#namespace_7 "Permanent link")
`string`[]
A list of strings representing the namespace path.
###### key[¶](#key_4 "Permanent link")
`string`
The unique identifier for the item.
###### options?[¶](#options_6 "Permanent link")
###### # refreshTtl?[¶](#refreshttl "Permanent link")
`null` | `boolean`
Whether to refresh the TTL on this read operation. If null, uses the store's default behavior.
##### Returns[¶](#returns_38 "Permanent link")
`Promise`\<`null` | `Item`>
Promise
##### Example[¶](#example "Permanent link")
```
const item = await client.store.getItem(
  ["documents", "user123"],
  "item456",
  { refreshTtl: true }
);
console.log(item);
// {
//   namespace: ["documents", "user123"],
//   key: "item456",
//   value: { title: "My Document", content: "Hello World" },
//   createdAt: "2024-07-30T12:00:00Z",
//   updatedAt: "2024-07-30T12:00:00Z"
// }
```
---
#### listNamespaces()[¶](#listnamespaces "Permanent link")
> **listNamespaces**(`options`?): `Promise`\<`ListNamespaceResponse`>
Defined in: [client.ts:1392](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1392)
List namespaces with optional match conditions.
##### Parameters[¶](#parameters_38 "Permanent link")
###### options?[¶](#options_7 "Permanent link")
###### # limit?[¶](#limit_9 "Permanent link")
`number`
Maximum number of namespaces to return (default is 100).
###### # maxDepth?[¶](#maxdepth "Permanent link")
`number`
Optional integer specifying the maximum depth of namespaces to return.
###### # offset?[¶](#offset_9 "Permanent link")
`number`
Number of namespaces to skip before returning results (default is 0).
###### # prefix?[¶](#prefix "Permanent link")
`string`[]
Optional list of strings representing the prefix to filter namespaces.
###### # suffix?[¶](#suffix_1 "Permanent link")
`string`[]
Optional list of strings representing the suffix to filter namespaces.
##### Returns[¶](#returns_39 "Permanent link")
`Promise`\<`ListNamespaceResponse`>
Promise
---
#### putItem()[¶](#putitem "Permanent link")
> **putItem**(`namespace`, `key`, `value`, `options`?): `Promise`\<`void`>
Defined in: [client.ts:1196](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1196)
Store or update an item.
##### Parameters[¶](#parameters_39 "Permanent link")
###### namespace[¶](#namespace_8 "Permanent link")
`string`[]
A list of strings representing the namespace path.
###### key[¶](#key_5 "Permanent link")
`string`
The unique identifier for the item within the namespace.
###### value[¶](#value_1 "Permanent link")
`Record`\<`string`, `any`>
A dictionary containing the item's data.
###### options?[¶](#options_8 "Permanent link")
###### # index?[¶](#index "Permanent link")
`null` | `false` | `string`[]
Controls search indexing - null (use defaults), false (disable), or list of field paths to index.
###### # ttl?[¶](#ttl "Permanent link")
`null` | `number`
Optional time-to-live in minutes for the item, or null for no expiration.
##### Returns[¶](#returns_40 "Permanent link")
`Promise`\<`void`>
Promise
##### Example[¶](#example_1 "Permanent link")
```
await client.store.putItem(
  ["documents", "user123"],
  "item456",
  { title: "My Document", content: "Hello World" },
  { ttl: 60 } // expires in 60 minutes
);
```
---
#### searchItems()[¶](#searchitems "Permanent link")
> **searchItems**(`namespacePrefix`, `options`?): `Promise`\<`SearchItemsResponse`>
Defined in: [client.ts:1347](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L1347)
Search for items within a namespace prefix.
##### Parameters[¶](#parameters_40 "Permanent link")
###### namespacePrefix[¶](#namespaceprefix "Permanent link")
`string`[]
List of strings representing the namespace prefix.
###### options?[¶](#options_9 "Permanent link")
###### # filter?[¶](#filter_1 "Permanent link")
`Record`\<`string`, `any`>
Optional dictionary of key-value pairs to filter results.
###### # limit?[¶](#limit_10 "Permanent link")
`number`
Maximum number of items to return (default is 10).
###### # offset?[¶](#offset_10 "Permanent link")
`number`
Number of items to skip before returning results (default is 0).
###### # query?[¶](#query_3 "Permanent link")
`string`
Optional search query.
###### # refreshTtl?[¶](#refreshttl_1 "Permanent link")
`null` | `boolean`
Whether to refresh the TTL on items returned by this search. If null, uses the store's default behavior.
##### Returns[¶](#returns_41 "Permanent link")
`Promise`\<`SearchItemsResponse`>
Promise
##### Example[¶](#example_2 "Permanent link")
```
const results = await client.store.searchItems(
  ["documents"],
  {
    filter: { author: "John Doe" },
    limit: 5,
    refreshTtl: true
  }
);
console.log(results);
// {
//   items: [
//     {
//       namespace: ["documents", "user123"],
//       key: "item789",
//       value: { title: "Another Document", author: "John Doe" },
//       createdAt: "2024-07-30T12:00:00Z",
//       updatedAt: "2024-07-30T12:00:00Z"
//     },
//     // ... additional items ...
//   ]
// }
```
[**@langchain/langgraph-sdk**](#readmemd)
---
[@langchain/langgraph-sdk](#readmemd) / ThreadsClient
## Class: ThreadsClient\<TStateType, TUpdateType>[¶](#class-threadsclienttstatetype-tupdatetype "Permanent link")
Defined in: [client.ts:489](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L489)
### Extends[¶](#extends_5 "Permanent link")
* `BaseClient`
### Type Parameters[¶](#type-parameters_8 "Permanent link")
• **TStateType** = `DefaultValues`
• **TUpdateType** = `TStateType`
### Constructors[¶](#constructors_7 "Permanent link")
#### new ThreadsClient()[¶](#new-threadsclient "Permanent link")
> **new ThreadsClient**\<`TStateType`, `TUpdateType`>(`config`?): [`ThreadsClient`](#classesthreadsclientmd)\<`TStateType`, `TUpdateType`>
Defined in: [client.ts:88](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L88)
##### Parameters[¶](#parameters_41 "Permanent link")
###### config?[¶](#config_9 "Permanent link")
[`ClientConfig`](#interfacesclientconfigmd)
##### Returns[¶](#returns_42 "Permanent link")
[`ThreadsClient`](#classesthreadsclientmd)\<`TStateType`, `TUpdateType`>
##### Inherited from[¶](#inherited-from_11 "Permanent link")
`BaseClient.constructor`
### Methods[¶](#methods_6 "Permanent link")
#### copy()[¶](#copy "Permanent link")
> **copy**(`threadId`): `Promise`\<`Thread`\<`TStateType`>>
Defined in: [client.ts:566](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L566)
Copy an existing thread
##### Parameters[¶](#parameters_42 "Permanent link")
###### threadId[¶](#threadid_13 "Permanent link")
`string`
ID of the thread to be copied
##### Returns[¶](#returns_43 "Permanent link")
`Promise`\<`Thread`\<`TStateType`>>
Newly copied thread
---
#### create()[¶](#create_3 "Permanent link")
> **create**(`payload`?): `Promise`\<`Thread`\<`TStateType`>>
Defined in: [client.ts:511](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L511)
Create a new thread.
##### Parameters[¶](#parameters_43 "Permanent link")
###### payload?[¶](#payload_12 "Permanent link")
Payload for creating a thread.
###### # graphId?[¶](#graphid_3 "Permanent link")
`string`
Graph ID to associate with the thread.
###### # ifExists?[¶](#ifexists_1 "Permanent link")
`OnConflictBehavior`
How to handle duplicate creation.
**Default**
```
"raise"
```
###### # metadata?[¶](#metadata_12 "Permanent link")
`Metadata`
Metadata for the thread.
###### # supersteps?[¶](#supersteps "Permanent link")
`object`[]
Apply a list of supersteps when creating a thread, each containing a sequence of updates.
Used for copying a thread between deployments.
###### # threadId?[¶](#threadid_14 "Permanent link")
`string`
ID of the thread to create.
If not provided, a random UUID will be generated.
##### Returns[¶](#returns_44 "Permanent link")
`Promise`\<`Thread`\<`TStateType`>>
The created thread.
---
#### delete()[¶](#delete_3 "Permanent link")
> **delete**(`threadId`): `Promise`\<`void`>
Defined in: [client.ts:599](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L599)
Delete a thread.
##### Parameters[¶](#parameters_44 "Permanent link")
###### threadId[¶](#threadid_15 "Permanent link")
`string`
ID of the thread.
##### Returns[¶](#returns_45 "Permanent link")
`Promise`\<`void`>
---
#### get()[¶](#get_2 "Permanent link")
> **get**\<`ValuesType`>(`threadId`): `Promise`\<`Thread`\<`ValuesType`>>
Defined in: [client.ts:499](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L499)
Get a thread by ID.
##### Type Parameters[¶](#type-parameters_9 "Permanent link")
• **ValuesType** = `TStateType`
##### Parameters[¶](#parameters_45 "Permanent link")
###### threadId[¶](#threadid_16 "Permanent link")
`string`
ID of the thread.
##### Returns[¶](#returns_46 "Permanent link")
`Promise`\<`Thread`\<`ValuesType`>>
The thread.
---
#### getHistory()[¶](#gethistory "Permanent link")
> **getHistory**\<`ValuesType`>(`threadId`, `options`?): `Promise`\<`ThreadState`\<`ValuesType`>[]>
Defined in: [client.ts:752](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L752)
Get all past states for a thread.
##### Type Parameters[¶](#type-parameters_10 "Permanent link")
• **ValuesType** = `TStateType`
##### Parameters[¶](#parameters_46 "Permanent link")
###### threadId[¶](#threadid_17 "Permanent link")
`string`
ID of the thread.
###### options?[¶](#options_10 "Permanent link")
Additional options.
###### # before?[¶](#before "Permanent link")
`Config`
###### # checkpoint?[¶](#checkpoint "Permanent link")
`Partial`\<`Omit`\<`Checkpoint`, `"thread_id"`>>
###### # limit?[¶](#limit_11 "Permanent link")
`number`
###### # metadata?[¶](#metadata_13 "Permanent link")
`Metadata`
##### Returns[¶](#returns_47 "Permanent link")
`Promise`\<`ThreadState`\<`ValuesType`>[]>
List of thread states.
---
#### getState()[¶](#getstate "Permanent link")
> **getState**\<`ValuesType`>(`threadId`, `checkpoint`?, `options`?): `Promise`\<`ThreadState`\<`ValuesType`>>
Defined in: [client.ts:659](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L659)
Get state for a thread.
##### Type Parameters[¶](#type-parameters_11 "Permanent link")
• **ValuesType** = `TStateType`
##### Parameters[¶](#parameters_47 "Permanent link")
###### threadId[¶](#threadid_18 "Permanent link")
`string`
ID of the thread.
###### checkpoint?[¶](#checkpoint_1 "Permanent link")
`string` | `Checkpoint`
###### options?[¶](#options_11 "Permanent link")
###### # subgraphs?[¶](#subgraphs "Permanent link")
`boolean`
##### Returns[¶](#returns_48 "Permanent link")
`Promise`\<`ThreadState`\<`ValuesType`>>
Thread state.
---
#### patchState()[¶](#patchstate "Permanent link")
> **patchState**(`threadIdOrConfig`, `metadata`): `Promise`\<`void`>
Defined in: [client.ts:722](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L722)
Patch the metadata of a thread.
##### Parameters[¶](#parameters_48 "Permanent link")
###### threadIdOrConfig[¶](#threadidorconfig "Permanent link")
Thread ID or config to patch the state of.
`string` | `Config`
###### metadata[¶](#metadata_14 "Permanent link")
`Metadata`
Metadata to patch the state with.
##### Returns[¶](#returns_49 "Permanent link")
`Promise`\<`void`>
---
#### search()[¶](#search_2 "Permanent link")
> **search**\<`ValuesType`>(`query`?): `Promise`\<`Thread`\<`ValuesType`>[]>
Defined in: [client.ts:611](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L611)
List threads
##### Type Parameters[¶](#type-parameters_12 "Permanent link")
• **ValuesType** = `TStateType`
##### Parameters[¶](#parameters_49 "Permanent link")
###### query?[¶](#query_4 "Permanent link")
Query options
###### # limit?[¶](#limit_12 "Permanent link")
`number`
Maximum number of threads to return.
Defaults to 10
###### # metadata?[¶](#metadata_15 "Permanent link")
`Metadata`
Metadata to filter threads by.
###### # offset?[¶](#offset_11 "Permanent link")
`number`
Offset to start from.
###### # sortBy?[¶](#sortby_1 "Permanent link")
`ThreadSortBy`
Sort by.
###### # sortOrder?[¶](#sortorder_1 "Permanent link")
`SortOrder`
Sort order.
Must be one of 'asc' or 'desc'.
###### # status?[¶](#status_5 "Permanent link")
`ThreadStatus`
Thread status to filter on.
Must be one of 'idle', 'busy', 'interrupted' or 'error'.
##### Returns[¶](#returns_50 "Permanent link")
`Promise`\<`Thread`\<`ValuesType`>[]>
List of threads
---
#### update()[¶](#update_1 "Permanent link")
> **update**(`threadId`, `payload`?): `Promise`\<`Thread`\<`DefaultValues`>>
Defined in: [client.ts:579](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L579)
Update a thread.
##### Parameters[¶](#parameters_50 "Permanent link")
###### threadId[¶](#threadid_19 "Permanent link")
`string`
ID of the thread.
###### payload?[¶](#payload_13 "Permanent link")
Payload for updating the thread.
###### # metadata?[¶](#metadata_16 "Permanent link")
`Metadata`
Metadata for the thread.
##### Returns[¶](#returns_51 "Permanent link")
`Promise`\<`Thread`\<`DefaultValues`>>
The updated thread.
---
#### updateState()[¶](#updatestate "Permanent link")
> **updateState**\<`ValuesType`>(`threadId`, `options`): `Promise`\<`Pick`\<`Config`, `"configurable"`>>
Defined in: [client.ts:693](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L693)
Add state to a thread.
##### Type Parameters[¶](#type-parameters_13 "Permanent link")
• **ValuesType** = `TUpdateType`
##### Parameters[¶](#parameters_51 "Permanent link")
###### threadId[¶](#threadid_20 "Permanent link")
`string`
The ID of the thread.
###### options[¶](#options_12 "Permanent link")
###### # asNode?[¶](#asnode "Permanent link")
`string`
###### # checkpoint?[¶](#checkpoint_2 "Permanent link")
`Checkpoint`
###### # checkpointId?[¶](#checkpointid "Permanent link")
`string`
###### # values[¶](#values_1 "Permanent link")
`ValuesType`
##### Returns[¶](#returns_52 "Permanent link")
`Promise`\<`Pick`\<`Config`, `"configurable"`>>
[**@langchain/langgraph-sdk**](#readmemd)
---
[@langchain/langgraph-sdk](#readmemd) / getApiKey
## Function: getApiKey()[¶](#function-getapikey "Permanent link")
> **getApiKey**(`apiKey`?): `undefined` | `string`
Defined in: [client.ts:53](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L53)
Get the API key from the environment.
Precedence:
1. explicit argument
2. LANGGRAPH\_API\_KEY
3. LANGSMITH\_API\_KEY
4. LANGCHAIN\_API\_KEY
### Parameters[¶](#parameters_52 "Permanent link")
#### apiKey?[¶](#apikey "Permanent link")
`string`
Optional API key provided as an argument
### Returns[¶](#returns_53 "Permanent link")
`undefined` | `string`
The API key if found, otherwise undefined
[**@langchain/langgraph-sdk**](#readmemd)
---
[@langchain/langgraph-sdk](#readmemd) / ClientConfig
## Interface: ClientConfig[¶](#interface-clientconfig "Permanent link")
Defined in: [client.ts:71](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L71)
### Properties[¶](#properties_3 "Permanent link")
#### apiKey?[¶](#apikey_1 "Permanent link")
> `optional` **apiKey**: `string`
Defined in: [client.ts:73](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L73)
---
#### apiUrl?[¶](#apiurl "Permanent link")
> `optional` **apiUrl**: `string`
Defined in: [client.ts:72](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L72)
---
#### callerOptions?[¶](#calleroptions "Permanent link")
> `optional` **callerOptions**: `AsyncCallerParams`
Defined in: [client.ts:74](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L74)
---
#### defaultHeaders?[¶](#defaultheaders "Permanent link")
> `optional` **defaultHeaders**: `Record`\<`string`, `undefined` | `null` | `string`>
Defined in: [client.ts:76](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L76)
---
#### timeoutMs?[¶](#timeoutms "Permanent link")
> `optional` **timeoutMs**: `number`
Defined in: [client.ts:75](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/client.ts#L75)
**[langchain/langgraph-sdk](https://github.com/langchain/langgraph-sdk "GitHub Repository: langchain/langgraph-sdk")**
---
## [langchain/langgraph-sdk](https://github.com/langchain/langgraph-sdk "GitHub Repository: langchain/langgraph-sdk")/react[¶](#langchainlanggraph-sdkreact "Permanent link")
### Interfaces[¶](#interfaces_2 "Permanent link")
* [UseStream](#reactinterfacesusestreammd)
* [UseStreamOptions](#reactinterfacesusestreamoptionsmd)
### Type Aliases[¶](#type-aliases_1 "Permanent link")
* [MessageMetadata](#reacttype-aliasesmessagemetadatamd)
### Functions[¶](#functions_1 "Permanent link")
* [useStream](#reactfunctionsusestreammd)
[**@langchain/langgraph-sdk**](#reactreadmemd)
---
[@langchain/langgraph-sdk](#reactreadmemd) / useStream
## Function: useStream()[¶](#function-usestream "Permanent link")
> **useStream**\<`StateType`, `Bag`>(`options`): [`UseStream`](#reactinterfacesusestreammd)\<`StateType`, `Bag`>
Defined in: [react/stream.tsx:618](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L618)
### Type Parameters[¶](#type-parameters_14 "Permanent link")
• **StateType** *extends* `Record`\<`string`, `unknown`> = `Record`\<`string`, `unknown`>
• **Bag** *extends* `object` = `BagTemplate`
### Parameters[¶](#parameters_53 "Permanent link")
#### options[¶](#options_13 "Permanent link")
[`UseStreamOptions`](#reactinterfacesusestreamoptionsmd)\<`StateType`, `Bag`>
### Returns[¶](#returns_54 "Permanent link")
[`UseStream`](#reactinterfacesusestreammd)\<`StateType`, `Bag`>
[**@langchain/langgraph-sdk**](#reactreadmemd)
---
[@langchain/langgraph-sdk](#reactreadmemd) / UseStream
## Interface: UseStream\<StateType, Bag>[¶](#interface-usestreamstatetype-bag "Permanent link")
Defined in: [react/stream.tsx:507](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L507)
### Type Parameters[¶](#type-parameters_15 "Permanent link")
• **StateType** *extends* `Record`\<`string`, `unknown`> = `Record`\<`string`, `unknown`>
• **Bag** *extends* `BagTemplate` = `BagTemplate`
### Properties[¶](#properties_4 "Permanent link")
#### assistantId[¶](#assistantid_17 "Permanent link")
> **assistantId**: `string`
Defined in: [react/stream.tsx:592](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L592)
The ID of the assistant to use.
---
#### branch[¶](#branch "Permanent link")
> **branch**: `string`
Defined in: [react/stream.tsx:542](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L542)
The current branch of the thread.
---
#### client[¶](#client "Permanent link")
> **client**: `Client`
Defined in: [react/stream.tsx:587](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L587)
LangGraph SDK client used to send request and receive responses.
---
#### error[¶](#error "Permanent link")
> **error**: `unknown`
Defined in: [react/stream.tsx:519](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L519)
Last seen error from the thread or during streaming.
---
#### experimental\_branchTree[¶](#experimental_branchtree "Permanent link")
> **experimental\_branchTree**: `Sequence`\<`StateType`>
Defined in: [react/stream.tsx:558](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L558)
**`Experimental`**
Tree of all branches for the thread.
---
#### getMessagesMetadata()[¶](#getmessagesmetadata "Permanent link")
> **getMessagesMetadata**: (`message`, `index`?) => `undefined` | [`MessageMetadata`](#reacttype-aliasesmessagemetadatamd)\<`StateType`>
Defined in: [react/stream.tsx:579](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L579)
Get the metadata for a message, such as first thread state the message
was seen in and branch information.
##### Parameters[¶](#parameters_54 "Permanent link")
###### message[¶](#message_2 "Permanent link")
`Message`
The message to get the metadata for.
###### index?[¶](#index_1 "Permanent link")
`number`
The index of the message in the thread.
##### Returns[¶](#returns_55 "Permanent link")
`undefined` | [`MessageMetadata`](#reacttype-aliasesmessagemetadatamd)\<`StateType`>
The metadata for the message.
---
#### history[¶](#history "Permanent link")
> **history**: `ThreadState`\<`StateType`>[]
Defined in: [react/stream.tsx:552](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L552)
Flattened history of thread states of a thread.
---
#### interrupt[¶](#interrupt "Permanent link")
> **interrupt**: `undefined` | `Interrupt`\<`GetInterruptType`\<`Bag`>>
Defined in: [react/stream.tsx:563](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L563)
Get the interrupt value for the stream if interrupted.
---
#### isLoading[¶](#isloading "Permanent link")
> **isLoading**: `boolean`
Defined in: [react/stream.tsx:524](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L524)
Whether the stream is currently running.
---
#### messages[¶](#messages "Permanent link")
> **messages**: `Message`[]
Defined in: [react/stream.tsx:569](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L569)
Messages inferred from the thread.
Will automatically update with incoming message chunks.
---
#### setBranch()[¶](#setbranch "Permanent link")
> **setBranch**: (`branch`) => `void`
Defined in: [react/stream.tsx:547](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L547)
Set the branch of the thread.
##### Parameters[¶](#parameters_55 "Permanent link")
###### branch[¶](#branch_1 "Permanent link")
`string`
##### Returns[¶](#returns_56 "Permanent link")
`void`
---
#### stop()[¶](#stop "Permanent link")
> **stop**: () => `void`
Defined in: [react/stream.tsx:529](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L529)
Stops the stream.
##### Returns[¶](#returns_57 "Permanent link")
`void`
---
#### submit()[¶](#submit "Permanent link")
> **submit**: (`values`, `options`?) => `void`
Defined in: [react/stream.tsx:534](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L534)
Create and stream a run to the thread.
##### Parameters[¶](#parameters_56 "Permanent link")
###### values[¶](#values_2 "Permanent link")
`undefined` | `null` | `GetUpdateType`\<`Bag`, `StateType`>
###### options?[¶](#options_14 "Permanent link")
`SubmitOptions`\<`StateType`, `GetConfigurableType`\<`Bag`>>
##### Returns[¶](#returns_58 "Permanent link")
`void`
---
#### values[¶](#values_3 "Permanent link")
> **values**: `StateType`
Defined in: [react/stream.tsx:514](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L514)
The current values of the thread.
[**@langchain/langgraph-sdk**](#reactreadmemd)
---
[@langchain/langgraph-sdk](#reactreadmemd) / UseStreamOptions
## Interface: UseStreamOptions\<StateType, Bag>[¶](#interface-usestreamoptionsstatetype-bag "Permanent link")
Defined in: [react/stream.tsx:408](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L408)
### Type Parameters[¶](#type-parameters_16 "Permanent link")
• **StateType** *extends* `Record`\<`string`, `unknown`> = `Record`\<`string`, `unknown`>
• **Bag** *extends* `BagTemplate` = `BagTemplate`
### Properties[¶](#properties_5 "Permanent link")
#### apiKey?[¶](#apikey_2 "Permanent link")
> `optional` **apiKey**: `string`
Defined in: [react/stream.tsx:430](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L430)
The API key to use.
---
#### apiUrl?[¶](#apiurl_1 "Permanent link")
> `optional` **apiUrl**: `string`
Defined in: [react/stream.tsx:425](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L425)
The URL of the API to use.
---
#### assistantId[¶](#assistantid_18 "Permanent link")
> **assistantId**: `string`
Defined in: [react/stream.tsx:415](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L415)
The ID of the assistant to use.
---
#### callerOptions?[¶](#calleroptions_1 "Permanent link")
> `optional` **callerOptions**: `AsyncCallerParams`
Defined in: [react/stream.tsx:435](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L435)
Custom call options, such as custom fetch implementation.
---
#### client?[¶](#client_1 "Permanent link")
> `optional` **client**: `Client`\<`DefaultValues`, `DefaultValues`, `unknown`>
Defined in: [react/stream.tsx:420](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L420)
Client used to send requests.
---
#### defaultHeaders?[¶](#defaultheaders_1 "Permanent link")
> `optional` **defaultHeaders**: `Record`\<`string`, `undefined` | `null` | `string`>
Defined in: [react/stream.tsx:440](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L440)
Default headers to send with requests.
---
#### messagesKey?[¶](#messageskey "Permanent link")
> `optional` **messagesKey**: `string`
Defined in: [react/stream.tsx:448](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L448)
Specify the key within the state that contains messages.
Defaults to "messages".
##### Default[¶](#default "Permanent link")
```
"messages"
```
---
#### onCustomEvent()?[¶](#oncustomevent "Permanent link")
> `optional` **onCustomEvent**: (`data`, `options`) => `void`
Defined in: [react/stream.tsx:470](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L470)
Callback that is called when a custom event is received.
##### Parameters[¶](#parameters_57 "Permanent link")
###### data[¶](#data "Permanent link")
`GetCustomEventType`\<`Bag`>
###### options[¶](#options_15 "Permanent link")
###### # mutate[¶](#mutate "Permanent link")
(`update`) => `void`
##### Returns[¶](#returns_59 "Permanent link")
`void`
---
#### onDebugEvent()?[¶](#ondebugevent "Permanent link")
> `optional` **onDebugEvent**: (`data`) => `void`
Defined in: [react/stream.tsx:494](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L494)
**`Internal`**
Callback that is called when a debug event is received.
This API is experimental and subject to change.
##### Parameters[¶](#parameters_58 "Permanent link")
###### data[¶](#data_1 "Permanent link")
`unknown`
##### Returns[¶](#returns_60 "Permanent link")
`void`
---
#### onError()?[¶](#onerror "Permanent link")
> `optional` **onError**: (`error`) => `void`
Defined in: [react/stream.tsx:453](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L453)
Callback that is called when an error occurs.
##### Parameters[¶](#parameters_59 "Permanent link")
###### error[¶](#error_1 "Permanent link")
`unknown`
##### Returns[¶](#returns_61 "Permanent link")
`void`
---
#### onFinish()?[¶](#onfinish "Permanent link")
> `optional` **onFinish**: (`state`) => `void`
Defined in: [react/stream.tsx:458](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L458)
Callback that is called when the stream is finished.
##### Parameters[¶](#parameters_60 "Permanent link")
###### state[¶](#state "Permanent link")
`ThreadState`\<`StateType`>
##### Returns[¶](#returns_62 "Permanent link")
`void`
---
#### onLangChainEvent()?[¶](#onlangchainevent "Permanent link")
> `optional` **onLangChainEvent**: (`data`) => `void`
Defined in: [react/stream.tsx:488](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L488)
Callback that is called when a LangChain event is received.
##### Parameters[¶](#parameters_61 "Permanent link")
###### data[¶](#data_2 "Permanent link")
###### # data[¶](#data_3 "Permanent link")
`unknown`
###### # event[¶](#event_1 "Permanent link")
`string` & `object` | `"on_tool_start"` | `"on_tool_stream"` | `"on_tool_end"` | `"on_chat_model_start"` | `"on_chat_model_stream"` | `"on_chat_model_end"` | `"on_llm_start"` | `"on_llm_stream"` | `"on_llm_end"` | `"on_chain_start"` | `"on_chain_stream"` | `"on_chain_end"` | `"on_retriever_start"` | `"on_retriever_stream"` | `"on_retriever_end"` | `"on_prompt_start"` | `"on_prompt_stream"` | `"on_prompt_end"`
###### # metadata[¶](#metadata_17 "Permanent link")
`Record`\<`string`, `unknown`>
###### # name[¶](#name_5 "Permanent link")
`string`
###### # parent\_ids[¶](#parent_ids "Permanent link")
`string`[]
###### # run\_id[¶](#run_id_2 "Permanent link")
`string`
###### # tags[¶](#tags "Permanent link")
`string`[]
##### Returns[¶](#returns_63 "Permanent link")
`void`
##### See[¶](#see_1 "Permanent link")
<https://langchain-ai.github.io/langgraph/cloud/how-tos/stream_events/#stream-graph-in-events-mode> for more details.
---
#### onMetadataEvent()?[¶](#onmetadataevent "Permanent link")
> `optional` **onMetadataEvent**: (`data`) => `void`
Defined in: [react/stream.tsx:482](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L482)
Callback that is called when a metadata event is received.
##### Parameters[¶](#parameters_62 "Permanent link")
###### data[¶](#data_4 "Permanent link")
###### # run\_id[¶](#run_id_3 "Permanent link")
`string`
###### # thread\_id[¶](#thread_id_8 "Permanent link")
`string`
##### Returns[¶](#returns_64 "Permanent link")
`void`
---
#### onThreadId()?[¶](#onthreadid "Permanent link")
> `optional` **onThreadId**: (`threadId`) => `void`
Defined in: [react/stream.tsx:504](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L504)
Callback that is called when the thread ID is updated (ie when a new thread is created).
##### Parameters[¶](#parameters_63 "Permanent link")
###### threadId[¶](#threadid_21 "Permanent link")
`string`
##### Returns[¶](#returns_65 "Permanent link")
`void`
---
#### onUpdateEvent()?[¶](#onupdateevent "Permanent link")
> `optional` **onUpdateEvent**: (`data`) => `void`
Defined in: [react/stream.tsx:463](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L463)
Callback that is called when an update event is received.
##### Parameters[¶](#parameters_64 "Permanent link")
###### data[¶](#data_5 "Permanent link")
##### Returns[¶](#returns_66 "Permanent link")
`void`
---
#### threadId?[¶](#threadid_22 "Permanent link")
> `optional` **threadId**: `null` | `string`
Defined in: [react/stream.tsx:499](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L499)
The ID of the thread to fetch history and current values from.
[**@langchain/langgraph-sdk**](#reactreadmemd)
---
[@langchain/langgraph-sdk](#reactreadmemd) / MessageMetadata
## Type Alias: MessageMetadata\<StateType>[¶](#type-alias-messagemetadatastatetype "Permanent link")
> **MessageMetadata**\<`StateType`>: `object`
Defined in: [react/stream.tsx:169](https://github.com/langchain-ai/langgraph/blob/d4f644877db6264bd46d0b00fc4c37f174e502d5/libs/sdk-js/src/react/stream.tsx#L169)
### Type Parameters[¶](#type-parameters_17 "Permanent link")
• **StateType** *extends* `Record`\<`string`, `unknown`>
### Type declaration[¶](#type-declaration "Permanent link")
#### branch[¶](#branch_2 "Permanent link")
> **branch**: `string` | `undefined`
The branch of the message.
#### branchOptions[¶](#branchoptions "Permanent link")
> **branchOptions**: `string`[] | `undefined`
The list of branches this message is part of.
This is useful for displaying branching controls.
#### firstSeenState[¶](#firstseenstate "Permanent link")
> **firstSeenState**: `ThreadState`\<`StateType`> | `undefined`
The first thread state the message was seen in.
#### messageId[¶](#messageid "Permanent link")
> **messageId**: `string`
The ID of the message used.
Back to top

[Source](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/js_ts_sdk_ref/)
