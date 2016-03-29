{
  "title": "Event stream '$settings'",
  "id": "http://fake-eventstore.com:12345/streams/%24settings",
  "updated": "2016-03-24T16:00:26.709779Z",
  "streamId": "$settings",
  "author": {
    "name": "EventStore"
  },
  "headOfStream": true,
  "selfUrl": "http://fake-eventstore.com:12345/streams/%24settings",
  "eTag": "0;248368668",
  "links": [
    {
      "uri": "http://fake-eventstore.com:12345/streams/%24settings",
      "relation": "self"
    },
    {
      "uri": "http://fake-eventstore.com:12345/streams/%24settings/head/backward/20",
      "relation": "first"
    },
    {
      "uri": "http://fake-eventstore.com:12345/streams/%24settings/1/forward/20",
      "relation": "previous"
    },
    {
      "uri": "http://fake-eventstore.com:12345/streams/%24settings/metadata",
      "relation": "metadata"
    }
  ],
  "entries": [
    {
      "title": "0@$settings",
      "id": "http://fake-eventstore.com:12345/streams/%24settings/0",
      "updated": "2016-03-24T16:00:26.709779Z",
      "author": {
        "name": "EventStore"
      },
      "summary": "settings",
      "links": [
        {
          "uri": "http://fake-eventstore.com:12345/streams/%24settings/0",
          "relation": "edit"
        },
        {
          "uri": "http://fake-eventstore.com:12345/streams/%24settings/0",
          "relation": "alternate"
        }
      ]
    }
  ]
}
