Please add your submission content here.
.
├── flight-manifest-csv       # flight information for each passenger
├── boarding_pass_template    # sample boarding passes for the passengers listed in the manifest table
├── digital_id_template       # sample digital IDs (California Driver License) for the passengers listed in the manifest table
└── digital-video-sample      # a sample video to perform face verification by comparing it with the digital ID
# Type of validation 
- DoBValidation: id + boarding pass
- PersonValidation: id + video
- LuggageValidation:
- NameValidation: id + boarding pass
- BoardingPassValidation: boarding pass + flight manifest
