from utils import Location

ONTOLOGY = 'sharing'

SERVICES = [(Location(0, 0), {
                'information-broker': 'information-broker-1@localhost',
                'review-collector': 'review-collector-1@localhost',
                'product-vault': 'product-vault-1@localhost'
            }),
            (Location(100, 100), {
                'information-broker': 'information-broker-2@localhost',
                'review-collector': 'review-collector-2@localhost',
                'product-vault': 'product-vault-2@localhost'
            })
          ]

BROKER_DIRECTORY_JID = 'broker-directory@localhost'