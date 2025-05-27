#!/bin/bash
# Configuration
SYMID="000123456789"  # Your PowerMax serial number
OUTPUT_DIR="/tmp/rdf_reports"
BATCH_SIZE=25

# Create output directory
mkdir -p $OUTPUT_DIR

# Get list of all RDF device groups
symrdf -sid $SYMID list > $OUTPUT_DIR/all_rdf_groups.txt

# Extract group names and split into batches
awk '/Group Name:/ {print $3}' $OUTPUT_DIR/all_rdf_groups.txt > $OUTPUT_DIR/group_list.txt
split -l $BATCH_SIZE $OUTPUT_DIR/group_list.txt $OUTPUT_DIR/batch_

# Process each batch
for batch in $OUTPUT_DIR/batch_*; do
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  BATCH_NAME=$(basename $batch)
  REPORT_FILE="$OUTPUT_DIR/rdf_status_${BATCH_NAME}_${TIMESTAMP}.csv"
  
  # Create CSV header
  echo "Group Name,State,RDF Mode,Volume Config,RA Group,RA Capacity" > $REPORT_FILE
  
  # Process each group in the batch
  while read -r group; do
    echo "Processing group: $group"
    
    # Get detailed RDF info and parse key metrics
    symrdf -sid $SYMID -g $group query > $OUTPUT_DIR/temp.txt
    
    # Extract relevant information
    STATE=$(grep "RDF State" $OUTPUT_DIR/temp.txt | awk '{print $4}')
    MODE=$(grep "RDF Mode" $OUTPUT_DIR/temp.txt | awk '{print $4}')
    CONFIG=$(grep "Volume Config" $OUTPUT_DIR/temp.txt | awk '{print $4}')
    RA_GROUP=$(grep "RA Group" $OUTPUT_DIR/temp.txt | awk '{print $4}')
    RA_CAP=$(grep "RA Capacity" $OUTPUT_DIR/temp.txt | awk '{print $4}')
    
    # Append to CSV
    echo "$group,$STATE,$MODE,$CONFIG,$RA_GROUP,$RA_CAP" >> $REPORT_FILE
    
    # Optional delay between groups
    sleep 1
  done < $batch
  
  echo "Batch $BATCH_NAME completed. Report saved to $REPORT_FILE"
done

# Cleanup temporary files
rm $OUTPUT_DIR/temp.txt $OUTPUT_DIR/batch_*
echo "All batches processed. Reports available in $OUTPUT_DIR"
