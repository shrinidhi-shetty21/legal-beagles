PARTY_ADDITIONAL_FIELDS_JSON_SCHEMA = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "pageName": {
      "type": "string"
    },
    "additionalSourceData": {
      "type": "object",
      "properties": {
        "rawOrderedDataArray": {
          "type": "array",
          "items": [
            {
              "type": "object",
              "properties": {
                "lbl": {
                  "type": "string"
                },
                "val": {
                  "type": "string"
                },
                "ord": {
                  "type": "integer"
                },
                "childArray": {
                  "type": "array",
                  "items": {}
                }
              },
              "required": [
                "lbl",
                "val",
                "ord",
                "childArray"
              ]
            }
          ]
        }
      },
      "required": [
        "rawOrderedDataArray"
      ]
    }
  },
  "required": [
    "pageName",
    "additionalSourceData"
  ]
}
