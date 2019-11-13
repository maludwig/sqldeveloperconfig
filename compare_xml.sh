#!/bin/bash

FIRST_FILE="$1"
SECOND_FILE="$2"

function sanitize_xml {
  XML_PATH="$1"
  SANITARY_PATH="$2"
  cat "$XML_PATH" | sed -E 's/^ +//;s% />%/>%g' | sed -E 's/(className="[^"]*") (name="[^"]*")/\2 \1/' > "$SANITARY_PATH"
}

sanitize_xml "$FIRST_FILE" "$FIRST_FILE.sani.xml"
sanitize_xml "$SECOND_FILE" "$SECOND_FILE.sani.xml"
diff "$FIRST_FILE.sani.xml" "$SECOND_FILE.sani.xml"

