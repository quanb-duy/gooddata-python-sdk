# ChatRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**question** | **str** | User question | 
**chat_history_thread_id** | **str** | Chat History thread ID. Backend persists chat history and returns ID for further requests. | [optional] 
**limit_create** | **int** | Maximum number of created results. | [optional]  if omitted the server will use the default value of 3
**limit_create_context** | **int** | Maximum number of relevant objects included into context for LLM (for each object type). | [optional]  if omitted the server will use the default value of 10
**limit_search** | **int** | Maximum number of search results. | [optional]  if omitted the server will use the default value of 5
**relevant_score_threshold** | **float** | Score, above which we return found objects. Below this score objects are not relevant. | [optional]  if omitted the server will use the default value of 0.4
**search_score_threshold** | **float** | Score, above which we return found object(s) and don&#39;t call LLM to create new objects. | [optional]  if omitted the server will use the default value of 0.9
**title_to_descriptor_ratio** | **float** | Temporary for experiments. Ratio of title score to descriptor score. | [optional]  if omitted the server will use the default value of 0.7
**user_context** | [**UserContext**](UserContext.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

