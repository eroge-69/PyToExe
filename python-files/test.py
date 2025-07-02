          response_file = open (basePath+'response_msg/work/'+ShipmentReference+'_response_'+date+'.txt', 'w', newline = '\n' ) #this creates the response file
            response_file.write (response.text)
            response_file.close()
            request_file.close()
 
            response_str = json.loads(response.content)
            AWBNumber = response_str.get('shipmentTrackingNumber')# this extract the shipment ID from the json response
            documents = response_str.get('documents') # this extracts the list - documents
            LabelImage = [i["content"] for i in documents] # this extracts the dictionary from the list - documents
            label = LabelImage[0] # this remove the [ ] from the extracted base64 codes
            bytes = b64decode(label, validate=True) # this decode the base64 image
            f = open(basePath+'label/'+ShipmentReference+'_'+str(AWBNumber)+'.pdf', 'wb') #this save the decoded image as PDF file
            f.write(bytes)