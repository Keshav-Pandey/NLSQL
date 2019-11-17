using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Google.Cloud.Dialogflow.V2;
using Google.Protobuf;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace NLSQL.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class DialogflowController : ControllerBase
    {
        // A Protobuf JSON parser configured to ignore unknown fields. This makes
        // the action robust against new fields being introduced by Dialogflow.
        private static readonly JsonParser jsonParser =
            new JsonParser(JsonParser.Settings.Default.WithIgnoreUnknownFields(true));

        public ContentResult DialogAction([FromBody] WebhookRequest dialogflowRequest)
        {
            var intentName = dialogflowRequest.QueryResult.Intent.DisplayName;
            var actualQuestion = dialogflowRequest.QueryResult.QueryText;
            // Parse the body of the request using the Protobuf JSON parser,
            // *not* Json.NET.
            //WebhookRequest request;
            //using (var reader = new StreamReader(Request.Body))
            //{
            //    request = jsonParser.Parse<WebhookRequest>(reader);
            //}

            // Note: you should authenticate the request here.

            // Populate the response
            var testAnswer = $"Dialogflow Request for intent '{intentName}' and question '{actualQuestion}'";
            var dialogflowResponse = new WebhookResponse
            {
                FulfillmentText = testAnswer,
                FulfillmentMessages =
                { new Intent.Types.Message
                    { SimpleResponses = new Intent.Types.Message.Types.SimpleResponses
                        { SimpleResponses_ =
                            { new Intent.Types.Message.Types.SimpleResponse
                                {
                                   DisplayText = testAnswer,
                                   TextToSpeech = testAnswer,
                                }
                            }
                        }
                    }
            }

            };

            // Ask Protobuf to format the JSON to return.
            // Again, we don't want to use Json.NET - it doesn't know how to handle Struct
            // values etc.
            //string responseJson = dialogflowResponse.ToString();
            string json = "{ \"response\": \"reposnding from server weee!\", \"q\": \"" + actualQuestion + "\"," + "	\"fulfillmentText\": \"Fetching results\", \"fulfillmentMessages\": [{ \"text\": {\"text\": [\"" + actualQuestion + "\"			]}}] }";
            return Content(json, "application/json");
        }
    }
}