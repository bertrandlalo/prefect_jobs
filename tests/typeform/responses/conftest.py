import pytest


@pytest.fixture(scope='function')
def sandbox_form():
    form = {
        "id": "s1JOxF",
        "title": "Sandbox David for Iguazu",
        "theme": {
            "href": "https://api.typeform.com/themes/GKFi5U"
        },
        "workspace": {
            "href": "https://api.typeform.com/workspaces/10982280"
        },
        "settings": {
            "is_public": True,
            "is_trial": False,
            "language": "en",
            "progress_bar": "proportion",
            "show_progress_bar": True,
            "show_typeform_branding": True,
            "meta": {
                "allow_indexing": False
            }
        },
        "welcome_screens": [
            {
                "ref": "e5e7b3a0-00ba-420a-8d75-e27fb2ef8319",
                "title": "Welcome to my sandbox questionnaire",
                "properties": {
                    "show_button": True,
                    "button_text": "Start"
                },
                "attachment": {
                    "type": "image",
                    "href": "https://images.typeform.com/images/YNsJaQqJNLyj"
                }
            }
        ],
        "thankyou_screens": [
            {
                "ref": "81c6ac88-a573-43b9-b87f-23a042cc4188",
                "title": "Thank you for your patience!\nWe will use your data for testing purposes (mouahaha)",
                "properties": {
                    "show_button": False,
                    "share_icons": False,
                    "button_mode": "reload",
                    "button_text": "again"
                },
                "attachment": {
                    "type": "image",
                    "href": "https://images.typeform.com/images/Vv6xjf3pZvUQ"
                }
            },
            {
                "ref": "default_tys",
                "title": "Done! Your information was sent perfectly.",
                "properties": {
                    "show_button": False,
                    "share_icons": False
                }
            }
        ],
        "fields": [
            {
                "id": "rYgBYAwMJpie",
                "title": "What's your favourite color?",
                "ref": "ef7850f4-39d8-4097-bccf-e66fe8213af0",
                "properties": {
                    "description": "Question description here..",
                    "randomize": False,
                    "allow_multiple_selection": False,
                    "allow_other_choice": False,
                    "vertical_alignment": True,
                    "choices": [
                        {
                            "id": "Lyn9XeO6JpW4",
                            "ref": "94e14d99-0588-4229-aaf4-7a7e1374bb8d",
                            "label": "red"
                        },
                        {
                            "id": "bvqRqynMRsWK",
                            "ref": "1149b7b1-e400-4401-ab0f-4868361dd80a",
                            "label": "blue"
                        },
                        {
                            "id": "GJvEwH2nHaK4",
                            "ref": "332a15e8-5146-4917-882b-e520c9916c43",
                            "label": "green"
                        },
                        {
                            "id": "ecy3MjFhjmM5",
                            "ref": "5cfcd256-00d5-461f-b6e5-e1cca9d0a8fd",
                            "label": "black"
                        },
                        {
                            "id": "wbldlRLhO46X",
                            "ref": "5b60bc6d-9763-4bb3-838b-735aeb97adf8",
                            "label": "white"
                        }
                    ]
                },
                "validations": {
                    "required": True
                },
                "type": "multiple_choice"
            },
            {
                "id": "WvsHFdtymYCh",
                "title": "What are your favorite countries?",
                "ref": "4bebbb88-d7dc-42e3-9d49-9b2f21f7c1e1",
                "properties": {
                    "description": "You can choose one or more",
                    "randomize": True,
                    "allow_multiple_selection": True,
                    "allow_other_choice": False,
                    "vertical_alignment": True,
                    "choices": [
                        {
                            "id": "Qpd9bIM4VMPP",
                            "ref": "a69b0927-7661-49cb-a104-a6c9da6128e9",
                            "label": "France"
                        },
                        {
                            "id": "Ei8Vd7CdIYDy",
                            "ref": "fcde5300-f9f7-47ac-a1c9-172b8df23e2d",
                            "label": "USA"
                        },
                        {
                            "id": "jpxrmGlW94hM",
                            "ref": "c39fae20-d2b0-4c5a-9715-54a6b5bbede9",
                            "label": "Venezuela"
                        },
                        {
                            "id": "o4gb3rDFQBEj",
                            "ref": "32f9b31b-f957-407f-9c5a-c9e8d353da6b",
                            "label": "Germany"
                        },
                        {
                            "id": "rdS8upshRqed",
                            "ref": "34d15343-d697-44c8-b241-c424a3cf77ad",
                            "label": "South Africa"
                        },
                        {
                            "id": "Xe6AcIujrsiv",
                            "ref": "280d5cdd-e0b7-4ebc-bbda-6adc9a55b1b2",
                            "label": "Australia"
                        },
                        {
                            "id": "qsPZgZ4k1T1S",
                            "ref": "50d20cc5-26e9-4419-89ce-7edc60282648",
                            "label": "Mexico"
                        }
                    ]
                },
                "validations": {
                    "required": True,
                    "min_selection": 1
                },
                "type": "multiple_choice"
            },
            {
                "id": "PP23cM2vMRyf",
                "title": "What's the phone number of the president?",
                "ref": "662facb2-a017-4c3d-9ee9-3b842acda6d9",
                "properties": {
                    "description": "Just invent something",
                    "default_country_code": "FR"
                },
                "validations": {
                    "required": True
                },
                "type": "phone_number"
            },
            {
                "id": "nC5sjJJjw1LB",
                "title": "What's the best phrase from a movie?",
                "ref": "c09765e0-b114-4a33-9830-2dfab6c7a5f7",
                "properties": {
                    "description": "For example, \"I'll be back...\""
                },
                "validations": {
                    "required": True
                },
                "type": "short_text"
            },
            {
                "id": "RTLBwQSKHvFq",
                "title": "Write a poem here",
                "ref": "2f776b96-7552-4deb-9100-d2d3371e59a9",
                "properties": {
                    "description": "Roses are red, violets are blue. I heart you"
                },
                "validations": {
                    "required": True
                },
                "type": "long_text"
            },
            {
                "id": "skmAH4qbpOQP",
                "title": "Ok almost done!",
                "ref": "ee743367-c8d0-4172-951c-96427a874787",
                "properties": {
                    "hide_marks": False,
                    "button_text": "Continue"
                },
                "type": "statement"
            },
            {
                "id": "rsvT5CT4iUsF",
                "title": "What do you prefer?",
                "ref": "01f4efc3-ca52-4072-8392-cdfeeef035ee",
                "properties": {
                    "randomize": False,
                    "allow_multiple_selection": False,
                    "allow_other_choice": False,
                    "supersized": False,
                    "show_labels": True,
                    "choices": [
                        {
                            "id": "b1u1J6E2Ocqf",
                            "ref": "79fe15a1-e442-4c65-9622-04c04caa7dde",
                            "label": "Nature",
                            "attachment": {
                                "type": "image",
                                "href": "https://images.typeform.com/images/pzizgiqjcMYj"
                            }
                        },
                        {
                            "id": "P3ALO6vyI6Y2",
                            "ref": "590dbec6-cd99-4217-bc82-6d958e690f90",
                            "label": "Robots",
                            "attachment": {
                                "type": "image",
                                "href": "https://images.typeform.com/images/hXf8HW2JezUa"
                            }
                        },
                        {
                            "id": "p6wSUcUrqGdA",
                            "ref": "6e5c5317-9c9e-4532-96c4-0f90a2a8a001",
                            "label": "Fire",
                            "attachment": {
                                "type": "image",
                                "href": "https://images.typeform.com/images/W3Md7Nvrn63c"
                            }
                        },
                        {
                            "id": "bxfnrdUwBYdw",
                            "ref": "aeda196b-f5d6-42c8-8fea-c9c3423fddad",
                            "label": "Art",
                            "attachment": {
                                "type": "image",
                                "href": "https://images.typeform.com/images/xiCswjNABQDX"
                            }
                        }
                    ]
                },
                "validations": {
                    "required": True
                },
                "type": "picture_choice"
            },
            {
                "id": "f6EGCxnsZJLc",
                "title": "Would you buy a plumbus?",
                "ref": "a3a7416b-868b-4cb3-aa1d-59879297869f",
                "properties": {
                    "description": "If you don't know what a plumbus is, then answer randomly"
                },
                "validations": {
                    "required": True
                },
                "type": "yes_no"
            },
            {
                "id": "TauISOgvK5Ak",
                "title": "Write a random email address",
                "ref": "09b03ba0-479d-4b47-ab11-9445272268cf",
                "validations": {
                    "required": True
                },
                "type": "email"
            },
            {
                "id": "JUasFMIqaakJ",
                "title": "On a scale of 1 to 10, how much is too much?",
                "ref": "b486a9e3-24cf-4b75-ab8d-1d7f811b5ca4",
                "properties": {
                    "steps": 11,
                    "start_at_one": True,
                    "labels": {
                        "left": "One",
                        "center": "Five",
                        "right": "Ten"
                    }
                },
                "validations": {
                    "required": True
                },
                "type": "opinion_scale"
            },
            {
                "id": "j1pNhX0Bw1Zv",
                "title": "What is the best number?",
                "ref": "65af85e5-aac2-481e-b100-2f9fc6c0fdc1",
                "properties": {
                    "steps": 5,
                    "start_at_one": False
                },
                "validations": {
                    "required": True
                },
                "type": "opinion_scale"
            },
            {
                "id": "XPVq4Oh49p64",
                "title": "Rate Jojo rabbit in a cat scale",
                "ref": "68e72c09-69bd-476f-8575-e3961cb040c2",
                "properties": {
                    "description": "If you did not see this movie, rate the latest movie you saw",
                    "steps": 7,
                    "shape": "cat"
                },
                "validations": {
                    "required": True
                },
                "type": "rating"
            },
            {
                "id": "o7KCGC0dEWIW",
                "title": "What's the best date for a date?",
                "ref": "2d08f7e2-e4ad-4731-a417-d4e80373ad8b",
                "properties": {
                    "structure": "DDMMYYYY",
                    "separator": "/"
                },
                "validations": {
                    "required": True
                },
                "type": "date"
            },
            {
                "id": "OVKSHSCfLjQH",
                "title": "How many M&M's colors exist?",
                "ref": "2c352954-2783-4dd1-9188-af3a7651ef1b",
                "validations": {
                    "required": True,
                    "min_value": 0,
                    "max_value": 100
                },
                "type": "number"
            },
            {
                "id": "syCaCTfuI1qL",
                "title": "What's the best shape?",
                "ref": "5e3ed6a9-d48e-4a5e-b12b-24263a4d2220",
                "properties": {
                    "alphabetical_order": False,
                    "randomize": True,
                    "choices": [
                        {
                            "label": "Circle"
                        },
                        {
                            "label": "Square"
                        },
                        {
                            "label": "Rectangle"
                        },
                        {
                            "label": "Blob"
                        },
                        {
                            "label": "Triangle"
                        },
                        {
                            "label": "Being out of shape"
                        }
                    ]
                },
                "validations": {
                    "required": True
                },
                "type": "dropdown"
            },
            {
                "id": "lwvf7v29z4yT",
                "title": "Do you agree to the legal terms?",
                "ref": "5ab15a57-7d05-4573-8ceb-70f2a5cb6b6a",
                "properties": {
                    "description": "We will not share your data.\nYou have to accept.\nYes."
                },
                "validations": {
                    "required": True
                },
                "type": "legal"
            },
            {
                "id": "BX25SQL9o3mx",
                "title": "This is a group of additional questions. Answer them as fast as possible",
                "ref": "7d7b3fb1-b627-4842-9042-2a3d04ac6c68",
                "properties": {
                    "show_button": True,
                    "button_text": "Continue",
                    "fields": [
                        {
                            "id": "aZIQsDPWEFZv",
                            "title": "English, do you speak it?",
                            "ref": "80378af9-4594-47dd-9714-96602a549fc4",
                            "validations": {
                                "required": False
                            },
                            "type": "yes_no"
                        },
                        {
                            "id": "R1vDNltsxSAY",
                            "title": "1+1+1+1",
                            "ref": "fc4cc535-94ad-4933-a97f-f1d181c54b59",
                            "properties": {
                                "steps": 11,
                                "start_at_one": False
                            },
                            "validations": {
                                "required": False
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "DLbdhP0TjCdi",
                            "title": "Rate this questionnaire",
                            "ref": "e657f5c8-138b-42e0-817c-a344b36877e6",
                            "properties": {
                                "steps": 10,
                                "shape": "star"
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "rating"
                        },
                        {
                            "id": "xxaId6IgwcGm",
                            "title": "...",
                            "ref": "2783d30f-4c5c-414b-a7a3-79c94d9ee504",
                            "validations": {
                                "required": False
                            },
                            "type": "short_text"
                        }
                    ]
                },
                "type": "group"
            }
        ],
        "hidden": [
            "secret"
        ],
        "_links": {
            "display": "https://omind.typeform.com/to/s1JOxF"
        }
    }
    return form


@pytest.fixture(scope='function')
def sandbox_response():
    response = {
        "answers": [
            {
                "choice": {
                    "label": "black"
                },
                "field": {
                    "id": "rYgBYAwMJpie",
                    "ref": "ef7850f4-39d8-4097-bccf-e66fe8213af0",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "choices": {
                    "labels": [
                        "Venezuela",
                        "France",
                        "USA",
                        "Australia",
                        "South Africa",
                        "Germany"
                    ]
                },
                "field": {
                    "id": "WvsHFdtymYCh",
                    "ref": "4bebbb88-d7dc-42e3-9d49-9b2f21f7c1e1",
                    "type": "multiple_choice"
                },
                "type": "choices"
            },
            {
                "field": {
                    "id": "PP23cM2vMRyf",
                    "ref": "662facb2-a017-4c3d-9ee9-3b842acda6d9",
                    "type": "phone_number"
                },
                "phone_number": "+33646793147",
                "type": "phone_number"
            },
            {
                "field": {
                    "id": "nC5sjJJjw1LB",
                    "ref": "c09765e0-b114-4a33-9830-2dfab6c7a5f7",
                    "type": "short_text"
                },
                "text": "Great Scott!",
                "type": "text"
            },
            {
                "field": {
                    "id": "RTLBwQSKHvFq",
                    "ref": "2f776b96-7552-4deb-9100-d2d3371e59a9",
                    "type": "long_text"
                },
                "text": "Trololo",
                "type": "text"
            },
            {
                "choice": {
                    "label": "Robots"
                },
                "field": {
                    "id": "rsvT5CT4iUsF",
                    "ref": "01f4efc3-ca52-4072-8392-cdfeeef035ee",
                    "type": "picture_choice"
                },
                "type": "choice"
            },
            {
                "boolean": True,
                "field": {
                    "id": "f6EGCxnsZJLc",
                    "ref": "a3a7416b-868b-4cb3-aa1d-59879297869f",
                    "type": "yes_no"
                },
                "type": "boolean"
            },
            {
                "email": "david@two.con",
                "field": {
                    "id": "TauISOgvK5Ak",
                    "ref": "09b03ba0-479d-4b47-ab11-9445272268cf",
                    "type": "email"
                },
                "type": "email"
            },
            {
                "field": {
                    "id": "JUasFMIqaakJ",
                    "ref": "b486a9e3-24cf-4b75-ab8d-1d7f811b5ca4",
                    "type": "opinion_scale"
                },
                "number": 8,
                "type": "number"
            },
            {
                "field": {
                    "id": "j1pNhX0Bw1Zv",
                    "ref": "65af85e5-aac2-481e-b100-2f9fc6c0fdc1",
                    "type": "opinion_scale"
                },
                "number": 1,
                "type": "number"
            },
            {
                "field": {
                    "id": "XPVq4Oh49p64",
                    "ref": "68e72c09-69bd-476f-8575-e3961cb040c2",
                    "type": "rating"
                },
                "number": 4,
                "type": "number"
            },
            {
                "date": "2020-02-12T00:00:00.000Z",
                "field": {
                    "id": "o7KCGC0dEWIW",
                    "ref": "2d08f7e2-e4ad-4731-a417-d4e80373ad8b",
                    "type": "date"
                },
                "type": "date"
            },
            {
                "field": {
                    "id": "OVKSHSCfLjQH",
                    "ref": "2c352954-2783-4dd1-9188-af3a7651ef1b",
                    "type": "number"
                },
                "number": 54,
                "type": "number"
            },
            {
                "field": {
                    "id": "syCaCTfuI1qL",
                    "ref": "5e3ed6a9-d48e-4a5e-b12b-24263a4d2220",
                    "type": "dropdown"
                },
                "text": "Rectangle",
                "type": "text"
            },
            {
                "boolean": True,
                "field": {
                    "id": "lwvf7v29z4yT",
                    "ref": "5ab15a57-7d05-4573-8ceb-70f2a5cb6b6a",
                    "type": "legal"
                },
                "type": "boolean"
            },
            {
                "boolean": True,
                "field": {
                    "id": "aZIQsDPWEFZv",
                    "ref": "80378af9-4594-47dd-9714-96602a549fc4",
                    "type": "yes_no"
                },
                "type": "boolean"
            },
            {
                "field": {
                    "id": "R1vDNltsxSAY",
                    "ref": "fc4cc535-94ad-4933-a97f-f1d181c54b59",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "DLbdhP0TjCdi",
                    "ref": "e657f5c8-138b-42e0-817c-a344b36877e6",
                    "type": "rating"
                },
                "number": 8,
                "type": "number"
            },
            {
                "field": {
                    "id": "xxaId6IgwcGm",
                    "ref": "2783d30f-4c5c-414b-a7a3-79c94d9ee504",
                    "type": "short_text"
                },
                "text": "Ok",
                "type": "text"
            }
        ],
        "calculated": {
            "score": 0
        },
        "hidden": {
            "secret": "do2"
        },
        "landed_at": "2020-02-24T16:13:35Z",
        "landing_id": "5qp7tvw5a510pf5igdq0l3d5qp7t7q6w",
        "metadata": {
            "browser": "touch",
            "network_id": "87a888ee04",
            "platform": "mobile",
            "referer": "https://omind.typeform.com/to/s1JOxF?secret=do2",
            "user_agent": "Mozilla/5.0 (Linux; Android 9; ONEPLUS A5010) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.117 Mobile Safari/537.36"
        },
        "response_id": "5qp7tvw5a510pf5igdq0l3d5qp7t7q6w",
        "submitted_at": "2020-02-24T16:15:13Z",
        "token": "5qp7tvw5a510pf5igdq0l3d5qp7t7q6w"
    }
    return response


@pytest.fixture(scope='function')
def vr_form():
    form = {
        "id": "HoS3mL",
        "title": "Full individual questionnaire",
        "theme": {
            "href": "https://api.typeform.com/themes/PUZfPZ"
        },
        "workspace": {
            "href": "https://api.typeform.com/workspaces/10982280"
        },
        "settings": {
            "is_public": True,
            "is_trial": False,
            "language": "fr",
            "progress_bar": "percentage",
            "show_progress_bar": True,
            "show_typeform_branding": False,
            "meta": {
                "allow_indexing": False
            },
            "notifications": {
                "self": {
                    "recipients": [
                        "mickael@omind.me",
                        "nicolas@omind.me",
                        "floriane@omind.me"
                    ],
                    "subject": "Typeform: New response for {{form:title}}",
                    "message": "Your typeform {{form:title}} has a new response:\n\n{{form:all_answers}}\nLog in to view or download your responses at \n[https://admin.typeform.com/form/5900181/analyze/hash/results](https://admin.typeform.com/form/5900181/analyze/hash/results)\n{{link:report}}\nYou can turn off or configure self notifications for this typeform at \n[https://admin.typeform.com/form/5900181/configure/hash/self\\_notifications](https://admin.typeform.com/form/5900181/configure/hash/self\\_notifications)\n\nTeam Typeform\nAsk awesomely\n\nWant your responses automatically sent to a Google Sheet, MailChimp, Trello, or your own CRM? *Set up an integration to do that and much more:*\n[https://admin.typeform.com/form/5900181/configure/hash/integrations](https://admin.typeform.com/form/5900181/configure/hash/integrations)",
                    "enabled": True
                }
            }
        },
        "welcome_screens": [
            {
                "ref": "190694dac2431f61",
                "title": "*Bilan Cognitif, Comportemental et Emotionnel*",
                "properties": {
                    "show_button": True,
                    "button_text": "Je commence"
                },
                "attachment": {
                    "type": "image",
                    "href": "https://images.typeform.com/images/6BrGUyKWN4in"
                }
            }
        ],
        "thankyou_screens": [
            {
                "ref": "4d5d",
                "title": "Merci d'avoir répondu à ce questionnaire !\n\nCe bilan de personnalité sera complété par un bilan neurophysiologique en réalité virtuelle.\n\nNous vous communiquerons les résultats complets lors d'un entretien individualisé.",
                "properties": {
                    "show_button": False,
                    "share_icons": False,
                    "button_mode": "reload",
                    "button_text": "again"
                }
            },
            {
                "ref": "default_tys",
                "title": "Merci ! Vos informations ont parfaitement été envoyées.",
                "properties": {
                    "show_button": False,
                    "share_icons": False
                }
            }
        ],
        "fields": [
            {
                "id": "66524670",
                "title": "Mentions légales",
                "ref": "1b1d64b702825f3f",
                "properties": {
                    "description": "Les informations recueillies sur ce formulaire sont enregistrées de façon anonyme dans un fichier informatisé par la société Open Mind Innovation. \nElles sont conservées pendant 20 ans et sont destinées au département Recherche & Développement de la société.\nConformément à la loi « informatique et libertés », vous pouvez exercer votre droit d'accès aux données vous concernant et les faire rectifier en contactant notre DPO : dpo@omind.me"
                },
                "validations": {
                    "required": True
                },
                "type": "legal"
            },
            {
                "id": "67028424",
                "title": "Vous allez passer un bilan avec Open Mind Neurotechnologies, qu’est-ce qui vous fera dire que ce bilan aura été efficace ?",
                "ref": "42b72c68f027f50c",
                "validations": {
                    "required": True
                },
                "type": "long_text"
            },
            {
                "id": "66680785",
                "title": "Notre bilan vous permettra de mieux comprendre la façon dont vous gérez vos émotions au quotidien, en fonction de votre personnalité et de votre environnement.\n\nÀ travers une meilleure connaissance de vous-même, vous serez en mesure d'optimiser votre potentiel dans votre vie personnelle et professionnelle.",
                "ref": "d69c05473d4934ac",
                "properties": {
                    "hide_marks": True,
                    "button_text": "Continuer"
                },
                "type": "statement"
            },
            {
                "id": "66522629",
                "title": "Le questionnaire se présente sous la forme d'une succession de propositions. Pour chacune d'elle, vous allez devoir estimer dans quelle mesure celle-ci vous ressemble.\n\nIl est important que vous soyez honnête, il n'y a pas de \"\"bonne\"\" ou de \"\"mauvaise\"\" réponse. Si vous avez des difficultés sur une question particulière, essayez de répondre le plus spontanément possible. Dans la plupart des cas, la première réponse est la meilleure. Ne revenez plus sur vos réponses par la suite. \n\n*Le questionnaire prend environ 30 minutes.* N'hésitez pas à faire des pauses lorsque vous ressentez de la fatigue ou de la lassitude. *Dans ce cas, gardez bien la fenêtre de navigation ouverte. Vos réponse ne seront enregistrées que lorsque vous aurez terminé et validé le questionnaire.*",
                "ref": "e61c4018a0b7eb0d",
                "properties": {
                    "hide_marks": True,
                    "button_text": "Continuer"
                },
                "type": "statement"
            },
            {
                "id": "66527781",
                "title": "Sexe",
                "ref": "c1a31ab9186c2ffc",
                "properties": {
                    "randomize": False,
                    "allow_multiple_selection": False,
                    "allow_other_choice": False,
                    "vertical_alignment": False,
                    "choices": [
                        {
                            "id": "83111353",
                            "ref": "852aa7fd457de904",
                            "label": "Femme"
                        },
                        {
                            "id": "83111354",
                            "ref": "665cda4e27d60fcc",
                            "label": "Homme"
                        },
                        {
                            "id": "83111355",
                            "ref": "041e9bf3926300e8",
                            "label": "Autre"
                        }
                    ]
                },
                "validations": {
                    "required": True
                },
                "type": "multiple_choice"
            },
            {
                "id": "66528769",
                "title": "Année de naissance",
                "ref": "d5406020e2e8ac23",
                "properties": {
                    "description": "Veuillez saisir les 4 chiffres de votre année de naissance"
                },
                "validations": {
                    "required": True,
                    "min_value": 1900,
                    "max_value": 1999
                },
                "type": "number"
            },
            {
                "id": "66649641",
                "title": "*Appréciation du bien-être émotionnel, psychologique et social :*\n\nAu cours du mois passé, estimez combien de fois vous vous êtes senti·e ou vous avez senti...",
                "ref": "4021e2e74804fd2c",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66687419",
                            "title": "heureux·se",
                            "ref": "47373e16dfeb7d01",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83305195",
                                        "ref": "6f8611fb9e9b8255",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83305196",
                                        "ref": "bc61ebe760792e2f",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83305197",
                                        "ref": "d3d41aa9e04b1bb7",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83305198",
                                        "ref": "1a7174ee24ecedf7",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83305199",
                                        "ref": "2414d491f8e21741",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83305200",
                                        "ref": "876fe5c6312d2130",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708289",
                            "title": "intéressé·e par la vie",
                            "ref": "e53f0bc7317e6995",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83330823",
                                        "ref": "331adac6dbb1ffd9",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83330824",
                                        "ref": "a60537ca5405e1c8",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83330825",
                                        "ref": "1bc8626b44a1c8f2",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83330826",
                                        "ref": "576c3c48b6d1c719",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83330827",
                                        "ref": "4538c369e47e5594",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83330828",
                                        "ref": "49c9863f402795ec",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708326",
                            "title": "satisfait·e par la vie",
                            "ref": "7758bec371913adb",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83330889",
                                        "ref": "39544ec8c760daac",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83330890",
                                        "ref": "1568f489a9b42481",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83330891",
                                        "ref": "69ca85668d226c0a",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83330892",
                                        "ref": "a2b907b2803a2ae1",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83330893",
                                        "ref": "20c6f445e49296a0",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83330894",
                                        "ref": "f47dfcc2a946561b",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708352",
                            "title": "que vous contribuez significativement à la société",
                            "ref": "3e01e3861f317b64",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83330922",
                                        "ref": "d6a772a9afec4610",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83330923",
                                        "ref": "16870e9b92a04a2d",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83330924",
                                        "ref": "d7739492801e7e77",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83330925",
                                        "ref": "0b0efd3757335aa7",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83330926",
                                        "ref": "17f27763b3c86dc9",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83330927",
                                        "ref": "40dd048d7d3739be",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708446",
                            "title": "que vous appartenez à une communauté (groupe social, école, vie de quartier, etc...)",
                            "ref": "ddc572070aeec689",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331065",
                                        "ref": "32586a14fef6a559",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331066",
                                        "ref": "37b7629d7b47eaed",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331067",
                                        "ref": "974bb8e1d50d2be1",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331068",
                                        "ref": "bd367b4c350c0291",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331069",
                                        "ref": "54631c0934576920",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331070",
                                        "ref": "df8833d69556dd57",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708523",
                            "title": "que notre société est un bel endroit, ou tend à devenir meilleure, pour tout le monde",
                            "ref": "f109c3f45764ab61",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331236",
                                        "ref": "90e28e24ed113cbf",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331237",
                                        "ref": "40b895f474dda5f0",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331238",
                                        "ref": "b2c68ea5354e6e29",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331239",
                                        "ref": "b46c01cc9c2e0573",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331240",
                                        "ref": "51bd10d7564cf47c",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331241",
                                        "ref": "569801026df90cdb",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708558",
                            "title": "que les gens sont intrinsèquement bons",
                            "ref": "3c22d6b5c5394e79",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331271",
                                        "ref": "d67f62c1bfc155c2",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331272",
                                        "ref": "42cf47d59a0505d7",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331273",
                                        "ref": "5e23c50713b4b34c",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331274",
                                        "ref": "3de9e208d4f8e310",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331275",
                                        "ref": "5987024951d206a0",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331276",
                                        "ref": "f81305239fce8bfc",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708596",
                            "title": "que la manière dont notre société fonctionne a du sens pour vous",
                            "ref": "057b82c2e4dde124",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331310",
                                        "ref": "3913a47bd9d8711c",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331311",
                                        "ref": "5a13d6498ff6f6fc",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331312",
                                        "ref": "8810352dd5054c87",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331313",
                                        "ref": "11404e05d0b45692",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331314",
                                        "ref": "8e0225a3dc67635b",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331315",
                                        "ref": "d56edb6bbd31830b",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708624",
                            "title": "que globalement, vous aimez votre personnalité",
                            "ref": "c618a05dcef23bca",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331328",
                                        "ref": "1f5ca750aeadd884",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331329",
                                        "ref": "aa2c88ec5335d406",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331330",
                                        "ref": "c6cd2aab0fcbd6db",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331331",
                                        "ref": "da8dfc3099eac00e",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331332",
                                        "ref": "394e4bbde6cb86d4",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331333",
                                        "ref": "541788f9ebf8501c",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708834",
                            "title": "que vous arrivez à gérer vos responsabilités quotidiennes",
                            "ref": "3a66917386b1afeb",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331672",
                                        "ref": "9c60b6fa645bfdd5",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331673",
                                        "ref": "2c23a06d24f47102",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331674",
                                        "ref": "feba76e729cdd2ca",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331675",
                                        "ref": "850ff9be3e49d344",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331676",
                                        "ref": "d7b8e5439e1ec915",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331677",
                                        "ref": "768448f7e6f3f95d",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708898",
                            "title": "que vous avez des relations de confiance et chaleureuses avec les autres",
                            "ref": "1a02f69d82bd2b31",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331771",
                                        "ref": "e922d53b0c5004fe",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331772",
                                        "ref": "5806f12a34292b3a",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331773",
                                        "ref": "0b450857983689ba",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331774",
                                        "ref": "af6132784c54ded5",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331775",
                                        "ref": "7112325fde029ca2",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331776",
                                        "ref": "2d70452330a4877b",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66708927",
                            "title": "que vous vivez des expériences stimulantes qui vous font grandir et devenir quelqu'un de meilleur",
                            "ref": "ef1cf5df16810419",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331816",
                                        "ref": "d6a7e6bc27a35382",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331817",
                                        "ref": "424868caf0bf4b61",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331818",
                                        "ref": "d44bf829723f0086",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331819",
                                        "ref": "fde185e5f814fc78",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331820",
                                        "ref": "30210a1c254e0b7f",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331821",
                                        "ref": "191260f205f39f99",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66709006",
                            "title": "confiant·e pour penser ou exprimer vos propres idées et vos opinions",
                            "ref": "610255b27d463cb0",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331868",
                                        "ref": "8a873802cd1af9fe",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331869",
                                        "ref": "439f322af63c1fdd",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331870",
                                        "ref": "20b3838ad8ad228a",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331871",
                                        "ref": "48bac3ad02ea1525",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331872",
                                        "ref": "884679be88796be9",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331873",
                                        "ref": "596df2b95832bb4b",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        },
                        {
                            "id": "66709064",
                            "title": "que votre vie a un sens",
                            "ref": "848768bf553ff5e7",
                            "properties": {
                                "randomize": False,
                                "allow_multiple_selection": False,
                                "allow_other_choice": False,
                                "vertical_alignment": True,
                                "choices": [
                                    {
                                        "id": "83331955",
                                        "ref": "9022b95442135682",
                                        "label": "Jamais"
                                    },
                                    {
                                        "id": "83331956",
                                        "ref": "a95457a3a46d4af2",
                                        "label": "1 à 2 fois"
                                    },
                                    {
                                        "id": "83331957",
                                        "ref": "da6cb96fcd3bd586",
                                        "label": "1 fois par semaine"
                                    },
                                    {
                                        "id": "83331958",
                                        "ref": "c9bf137eace663fe",
                                        "label": "2-3 fois par semaine"
                                    },
                                    {
                                        "id": "83331959",
                                        "ref": "115d96fef7c66719",
                                        "label": "Presque tous les jours"
                                    },
                                    {
                                        "id": "83331960",
                                        "ref": "f0ba8bee2d6b65a3",
                                        "label": "Tous les jours"
                                    }
                                ]
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "multiple_choice"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "66784160",
                "title": "*Evaluation de la confiance en* *soi :*\n\nLes affirmations suivantes permettent d'appréhender votre confiance en vous. \nEn prenant en compte l'année écoulée, estimez à quel point celles-ci vous correspondent.",
                "ref": "796541ffa2b20b87",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66689224",
                            "title": "Je peux toujours arriver à résoudre mes difficultés si j'essaie assez fort.",
                            "ref": "08e0aab3c025aa19",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66689254",
                            "title": "Si quelqu'un s'oppose à moi, je peux trouver une façon d'obtenir ce que je veux.",
                            "ref": "b9ce88e88c7107d2",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66689501",
                            "title": "C'est facile pour moi de maintenir mon attention sur mes objectifs et atteindre mes buts.",
                            "ref": "2c36984e35e9b620",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66689526",
                            "title": "J'ai confiance dans le fait que je peux faire face efficacement aux événements inattendus.",
                            "ref": "eb62a550b68d93d4",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66689676",
                            "title": "Grâce à ma débrouillardise, je sais comment faire face aux situations imprévues.",
                            "ref": "9afcdc6328efc5d2",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66689694",
                            "title": "Je peux résoudre la plupart de mes problèmes si j'investis les efforts nécessaires.",
                            "ref": "265df217b391e127",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66689708",
                            "title": "Je peux rester calme lorsque je suis confronté·e à des difficultés car je peux me fier à mes habiletés pour faire face aux problèmes.",
                            "ref": "e35d48c3a5f5c45e",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66689847",
                            "title": "Lorsque je suis confronté·e à un problème, je peux habituellement trouver plusieurs solutions.",
                            "ref": "ac27f42869d120a2",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66690416",
                            "title": "Si je suis « coincé·e », je peux habituellement penser à ce que je pourrais faire.",
                            "ref": "780b7ea2c140bd78",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66690495",
                            "title": "Peu importe ce qui arrive, je suis généralement capable d'y faire face.",
                            "ref": "7c52a051dd1fdf20",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout vrai",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "66786209",
                "title": "*Échelle d'anxiété et de tolérance à l'incertitude :*\n\nLes affirmations suivantes concernent votre tolérance à la frustration et votre façon de gérer l'anxiété en général. \n\nBien que certaines questions soient proches, il y a des différences entre elles, et chacune doit être considérée comme une question indépendante des autres. La meilleure façon de procéder est de répondre assez rapidement.",
                "ref": "05433fe8a1bf8445",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66706984",
                            "title": "Les imprévus me dérangent énormément.",
                            "ref": "6be3d6ad406dcb8e",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707039",
                            "title": "Ça me frustre de ne pas avoir toute l'information dont j'ai besoin.",
                            "ref": "c9328836454bd690",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707057",
                            "title": "L'incertitude m'empêche de profiter pleinement de la vie.",
                            "ref": "993ecdfd0c9a5ec4",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707066",
                            "title": "On devrait tout prévenir pour éviter les surprises.",
                            "ref": "722835a0549afd5d",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707088",
                            "title": "Un léger imprévu peut tout gâcher, même la meilleure des planifications.",
                            "ref": "71cd4395aad46376",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707103",
                            "title": "Lorsqu'il est temps d'agir, l'incertitude me paralyse",
                            "ref": "cdf035e91c187449",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707126",
                            "title": "Lorsque je suis incertain·e, je ne peux pas aller de l'avant",
                            "ref": "0ed3437ad95761db",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707134",
                            "title": "Je veux toujours savoir ce que l'avenir me réserve.",
                            "ref": "aed5a9ea2ae59960",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707186",
                            "title": "Je déteste être pris·e au dépourvu",
                            "ref": "3a4203f0b22df1ea",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707208",
                            "title": "Le moindre doute peut m'empêcher d'agir.",
                            "ref": "9699bcee2f3f7d30",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707251",
                            "title": "Je devrais être capable de tout organiser à l'avance.",
                            "ref": "5eca865c9ed63399",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707264",
                            "title": "Je dois me retirer de toute situation incertaine.",
                            "ref": "ca77ccd1f7aaad41",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout correspondant",
                                    "center": "Assez correspondant",
                                    "right": "Tout à fait correspondant"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "66806037",
                "title": "*Évaluation de la disposition au bonheur :*\n\nLa disposition au bonheur se définit par sa capacité à apprécier les évènements positifs autour de soi. \nEstimez dans quelle mesure les propositions suivantes vous ressemblent.",
                "ref": "d14c28e5561f9e55",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66707656",
                            "title": "Quoique je fasse, le temps passe très vite.",
                            "ref": "9c468c7266fd3c94",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707659",
                            "title": "Ma vie sert un but plus élevé.",
                            "ref": "9d1d1e49966ff86f",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707686",
                            "title": "La vie est trop courte pour reporter les plaisirs qu'elle peut apporter.",
                            "ref": "95d9964ad2a9d7e0",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707697",
                            "title": "Je recherche des situations qui mettent au défi mes compétences et aptitudes.",
                            "ref": "3e2b29a8d17fe93c",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707704",
                            "title": "En choisissant que faire, je prends toujours en considération si d'autres personnes vont en bénéficier.",
                            "ref": "d7fb68d48239b52c",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707763",
                            "title": "Que ce soit au travail ou dans les loisirs j'ai généralement peu conscience de moi-même lorsque je suis concentré·e.",
                            "ref": "36ca651340f7ceab",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707779",
                            "title": "Je suis toujours très absorbé·e par ce que je fais.",
                            "ref": "eab3e5693041f64b",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707787",
                            "title": "Je recherche les occasions de me sentir euphorique.",
                            "ref": "90f442db38ee6549",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707833",
                            "title": "En choisissant que faire, je prends toujours en considération si je peux m'absorber dans l'activité.",
                            "ref": "c381c5a1615b0352",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707850",
                            "title": "Je suis rarement distrait·e par ce qui se passe autour de moi.",
                            "ref": "724da58bdf243133",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707898",
                            "title": "J'ai une responsabilité de faire du monde un endroit meilleur.",
                            "ref": "9e73c953b3a923be",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707926",
                            "title": "Ma vie a un sens durable.",
                            "ref": "240a501c576c0df8",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707951",
                            "title": "En choisissant que faire, je prends toujours en considération si ce sera agréable.",
                            "ref": "ded59d4c4e2c96d4",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66707959",
                            "title": "Ce que je fais a une importance pour la société.",
                            "ref": "62e5ea4cbd186476",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66708066",
                            "title": "Je suis d'accord avec cette affirmation : « La vie est courte, mange le dessert en premier ».",
                            "ref": "a5e5a047faf6f879",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66708154",
                            "title": "J'aime beaucoup faire des choses qui stimulent mes sens.",
                            "ref": "72bf007ebdd079b3",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66708170",
                            "title": "J'ai passé beaucoup de temps à réfléchir à ce que signifie la vie et comment je me situe globalement.",
                            "ref": "ecb9d1b076f99507",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66708177",
                            "title": "Pour moi, une bonne vie est une vie plaisante.",
                            "ref": "bbeb4c23008f2eff",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout comme moi",
                                    "right": "Tout à fait comme moi"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "66786804",
                "title": "*Échelle de réactivité émotionnelle :*\n\nLes affirmations suivantes décrivent des réactions émotionnelles variées. Estimez dans quelle mesure vous vous sentez en accord avec celles-ci.\n\nRappelez-vous qu'il est important de répondre aussi franchement et spontanément que possible. Il n’y a pas réponses de « justes » ou « fausses », « bonnes » ou « mauvaises ». C'est votre vécu personnel qui compte.",
                "ref": "f164ab24e1ade07c",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66710038",
                            "title": "J'ai tendance à être heureux·se très facilement.",
                            "ref": "9496c04b091aa795",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710041",
                            "title": "Mes émotions fluctuent systématiquement de neutres à positives.",
                            "ref": "87357f7f3121acec",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710102",
                            "title": "J'ai tendance à être très facilement enthousiaste à propos des choses.",
                            "ref": "fce9ad6e96ebad69",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710142",
                            "title": "Je me sens instantanément bien à propos des choses positives.",
                            "ref": "60cbf91a434603cd",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710171",
                            "title": "Je réagis très rapidement aux bonnes nouvelles.",
                            "ref": "9dd6e1c81d654a0b",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710194",
                            "title": "J'ai tendance à être très facilement contrarié·e.",
                            "ref": "8de24a09fb5f931e",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710207",
                            "title": "J'ai tendance à être très facilement déçu·e.",
                            "ref": "9ffd7add81988348",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710225",
                            "title": "J'ai tendance à être frustré·e très facilement.",
                            "ref": "91a446a9af8cb1a7",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710253",
                            "title": "Mes émotions passent très rapidement de neutres à négatives.",
                            "ref": "f6fa185b6f7355f3",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710259",
                            "title": "J'ai tendance à être très rapidement pessimiste à propos des choses négatives.",
                            "ref": "23565be5165e274d",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710279",
                            "title": "Lorsque je suis heureux·se, ce sentiment reste en moi pour un certain temps.",
                            "ref": "202f8f9d5e4f4d3b",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710349",
                            "title": "Lorsque je me sens positif·ve, je garde ce sentiment pour une bonne partie de la journée.",
                            "ref": "a99f2714a424d7d2",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710364",
                            "title": "Je peux rester enthousiaste pendant une longue période.",
                            "ref": "c724a3de7c82ff58",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710558",
                            "title": "Lorsque je reçois des nouvelles agréables, je reste heureux·se pendant un moment.",
                            "ref": "7f9f956e8f499134",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710564",
                            "title": "Lorsque quelqu'un me fait un compliment, cela améliore mon humeur pendant une longue période.",
                            "ref": "3cdaede9cb0dcb10",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710570",
                            "title": "Lorsque je suis contrarié·e, cela me prend un certain temps pour sortir de cet état.",
                            "ref": "07fb194f7f8de09e",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710935",
                            "title": "Cela me prend plus de temps que les autres personnes pour sortir d'un épisode de colère.",
                            "ref": "0cace96ac90577b7",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66710957",
                            "title": "Il m'est difficile de me remettre d'une frustration.",
                            "ref": "2513d19ea3ea55e6",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67064375",
                            "title": "Lorsque je suis de mauvaise humeur, c'est difficile d'en sortir.",
                            "ref": "0f2b1cc7eb53d5d7",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711012",
                            "title": "Lorsque je suis ennuyé·e par quelque chose, cela gâche complètement ma journée.",
                            "ref": "e59f6eeb559662d8",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711048",
                            "title": "Je pense que je ressens le bonheur plus intensément que mes amis.",
                            "ref": "68c1d595fe936ae6",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711058",
                            "title": "Lorsque je suis joyeux·se, j'ai tendance à le sentir très profondément.",
                            "ref": "d721d8e2e1c1d42d",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711085",
                            "title": "Je ressens les humeurs positives très profondément.",
                            "ref": "fe5812e40d89ae9b",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711104",
                            "title": "Lorsque je m'enthousiasme pour quelque chose, je ressens ce sentiment fortement.",
                            "ref": "94ea24871d07e14f",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711130",
                            "title": "Je ressens les sentiments positifs plus profondément que mes proches.",
                            "ref": "f81d8ef23e1709f0",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711187",
                            "title": "Si je suis contrarié·e, je le ressens plus intensément que les autres. ",
                            "ref": "ae3ca7cd9cd16b33",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711202",
                            "title": "La frustration est un sentiment que je ressens très profondément.",
                            "ref": "b769244e862847d4",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711230",
                            "title": "Lorsque je suis malheureux·se, je le ressens très fortement.",
                            "ref": "8891ce7bdaedbf21",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711240",
                            "title": "Lorsque je suis en colère, je le ressens fortement.",
                            "ref": "69a215b415a6ac64",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66711274",
                            "title": "Mes sentiments négatifs sont très intenses.",
                            "ref": "5da1d6341893121a",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Tout à fait en désaccord",
                                    "center": "Neutre",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "66806757",
                "title": "*Mesure des réactions en situation de challenge*\n\nLes énoncés suivants décrivent des attitudes et ressentis observables dans des situations difficiles. \nBien que certaines questions soient proches, il y a des différences entre elles, et chacune doit être considérée comme une question indépendante des autres. La meilleure façon de procéder est de répondre assez rapidement.",
                "ref": "18299e9cb9ba8f55",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66713510",
                            "title": "Je suis une personne qui prend les choses en main.",
                            "ref": "5cf1e55be91c0074",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66713525",
                            "title": "Je laisse les choses se résoudre d'elles-mêmes.",
                            "ref": "1d8ce68058a078d3",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66713942",
                            "title": "Après avoir atteint un but, j'en recherche un autre, plus stimulant.",
                            "ref": "704c4e5cad5525dc",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714059",
                            "title": "J'aime les défis et déjouer les pronostics.",
                            "ref": "a0f7963885491790",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714105",
                            "title": "J'imagine mes rêves et j'essaie de les atteindre.",
                            "ref": "7879757020cd9c81",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714119",
                            "title": "Malgré de nombreux contretemps, je réussis généralement à obtenir ce que je veux.",
                            "ref": "5d20ba1aa92bab1a",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714138",
                            "title": "J'essaie d'identifier en amont ce dont j'ai besoin pour réussir.",
                            "ref": "9abf2704be10509d",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714158",
                            "title": "J'essaie toujours de trouver un moyen de contourner les obstacles ; rien ne m'arrête vraiment.",
                            "ref": "66cb1a6b8f6354aa",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714210",
                            "title": "Je m'imagine souvent en situation d'échec donc je ne suis pas trop optimiste.",
                            "ref": "ae23abd0fadb2fd4",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714315",
                            "title": "Lorsque je postule à un emploi, je m'imagine déjà l'occuper.",
                            "ref": "394a9832ae171c98",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714335",
                            "title": "Je transforme les obstacles en expériences positives.",
                            "ref": "5431184ea56f0860",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714502",
                            "title": "Si quelqu'un me dit que je ne peux pas faire quelque chose, vous pouvez être sûr que je vais le faire.",
                            "ref": "85fcad1084061923",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714619",
                            "title": "Lorsque je rencontre un problème, je prends l'initiative de le résoudre.",
                            "ref": "40d43195d5f5a139",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714715",
                            "title": "Lorsque j'ai un problème, en général je m'imagine en situation d'échec.",
                            "ref": "a36f63651817f271",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66714637",
                            "title": "Je me sens capable de résoudre des problèmes difficiles.",
                            "ref": "b7427ccd4109eba1",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777041",
                            "title": "Plutôt que de réagir impulsivement, je réfléchis aux différentes manières de résoudre un problème.",
                            "ref": "5a61eeef16a97901",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777261",
                            "title": "Dans ma tête j'envisage plusieurs scénarios pour me préparer aux différentes issues possibles.",
                            "ref": "d58dc085db4d72a8",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777438",
                            "title": "J'aborde un problème en réfléchissant aux alternatives réalistes.",
                            "ref": "1d46638bbe5fca1d",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777446",
                            "title": "Lorsque j'ai un problème avec mes collègues, mes amis ou ma famille, j'imagine à l'avance comment je vais les résoudre.",
                            "ref": "8a4d91380b080a46",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777453",
                            "title": "Avant d'attaquer une tâche difficile, j'imagine différentes manières de l'accomplir.",
                            "ref": "d86bd5e2b324b2c3",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777471",
                            "title": "J'agis seulement après avoir réfléchi soigneusement au problème.",
                            "ref": "4d3870f4272feff3",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777556",
                            "title": "Je m'imagine résoudre un problème difficile avant de l'affronter réellement.",
                            "ref": "d88d380837d6bbf5",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777593",
                            "title": "J'aborde un problème sous différents angles jusqu'à ce que je trouve la solution.",
                            "ref": "d139814355bc5597",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777595",
                            "title": "Lorsqu'il y a un sérieux malentendu avec des collègues, des membres de ma famille ou des amis, je m'entraîne à la façon dont je vais les aborder.",
                            "ref": "888bd7dbeb46c2eb",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777712",
                            "title": "Je réfléchis à toutes les issues possibles à un problème avant de l'attaquer.",
                            "ref": "60045398d33c1e8f",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777730",
                            "title": "Je trouve souvent un moyen de décomposer des problèmes difficiles en éléments réalisables.",
                            "ref": "54fd8613d60edfe9",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777737",
                            "title": "J'établis un plan et je m'y tiens.",
                            "ref": "4b0eaa2d02d45103",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777750",
                            "title": "Je décompose un problème en plus petits éléments que je résous un par un.",
                            "ref": "5a2a7cb43d2f6982",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777843",
                            "title": "Je fais des listes et essaie de me concentrer sur les choses les plus importantes en premier.",
                            "ref": "1b67640780d61d1a",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777852",
                            "title": "Je planifie pour parer à différentes éventualités.",
                            "ref": "ff6698e23d7142f9",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777888",
                            "title": "Plutôt que de dépenser chaque centime que je gagne, je préfère économiser pour les mauvais jours.",
                            "ref": "7c7bf5718c0e56a1",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777955",
                            "title": "Je me prépare aux événements défavorables.",
                            "ref": "4ebccff60492ecb6",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66777998",
                            "title": "Je suis bien préparé·e pour les conséquences d'une catastrophe avant que celle-ci se produise.",
                            "ref": "c4246197bf464a46",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778039",
                            "title": "J'élabore mes stratégies pour modifier une situation avant d'agir.",
                            "ref": "9ff67fc7902a9d3d",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778132",
                            "title": "Je développe mes compétences professionnelles pour me prémunir du chômage.",
                            "ref": "3600db47fdaf4ac4",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778155",
                            "title": "Je m'assure que ma famille est bien prise en charge en cas d'adversité dans le futur.",
                            "ref": "592492ad2b595c35",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778171",
                            "title": "J'anticipe pour éviter les situations dangereuses.",
                            "ref": "93d8431cf45383fc",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778196",
                            "title": "Je planifie des stratégies en espérant obtenir le meilleur résultat possible.",
                            "ref": "b2976004bac37d0a",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778316",
                            "title": "J'essaie de bien gérer mon argent pour éviter d'être démuni·e dans mes vieux jours.",
                            "ref": "ebff4306c942b5d3",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778332",
                            "title": "Lorsque je résous mes propres problèmes, les conseils des autres peuvent m'être utiles.",
                            "ref": "cc20ba7ee8236fc2",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778530",
                            "title": "J'essaie de parler et d'expliquer mes problèmes de stress pour avoir l'avis de mes amis.",
                            "ref": "f4d3c0c50464bfa3",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778541",
                            "title": "Les informations provenant des autres m'ont souvent aidé·e à gérer mes propres problèmes.",
                            "ref": "c8657efc77f76b21",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778557",
                            "title": "En général, j'arrive à identifier les personnes qui sont en mesure de m'aider à développer mes propres solutions à un problème.",
                            "ref": "1340b50e9d8b7fcb",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778586",
                            "title": "Je demande aux autres ce qu'ils feraient dans ma situation.",
                            "ref": "011785d4e1de2136",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778592",
                            "title": "Parler aux autres peut être vraiment utile, cela permet de voir le problème sous un autre angle.",
                            "ref": "88d7c718663903fa",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778614",
                            "title": "J'appelle un ami pour parler d'un problème avant qu'il ne m'affecte trop.",
                            "ref": "b95f80c57a8d361b",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778646",
                            "title": "Lorsque j'ai des ennuis, je peux en général trouver une solution avec l'aide des autres.",
                            "ref": "f182e0833fa433db",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778681",
                            "title": "Si je me sens déprimé·e, je sais qui je peux appeler pour me sentir mieux.",
                            "ref": "1b8d806e719ff8fd",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778692",
                            "title": "Les autres m'aident à me sentir soutenu·e.",
                            "ref": "95a5ecf5133a46a2",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778700",
                            "title": "Je sais sur qui je peux compter dans les moments difficiles.",
                            "ref": "9ea0241175a177e8",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778745",
                            "title": "Lorsque je suis déprimé·e, je sors et j'en parle autour de moi.",
                            "ref": "e1bb383ebd4f79ce",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778756",
                            "title": "Je confie mes sentiments aux autres pour construire et maintenir des liens étroits.",
                            "ref": "aa1a88e424a1c318",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778842",
                            "title": "Lorsque j'ai un problème, j'aime laisser passer la nuit et dormir dessus.",
                            "ref": "e4fe610efee0c030",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778855",
                            "title": "Lorsqu'un problème est trop difficile, il m'arrive de le mettre de côté jusqu'à ce que je sois prêt·e à le gérer.",
                            "ref": "fb0450729e0be62c",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66778890",
                            "title": "Lorsque j'ai un problème, en général je le laisse de côté pendant un certain temps.",
                            "ref": "a7972bfcb8a9c0cd",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas vrai du tout",
                                    "right": "Tout à fait vrai"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "66807253",
                "title": "*Évaluation des besoins individuels en environnement professionnel :*\n\nCes affirmations concernent vos attitudes et ressentis spécifiquement dans le milieu professionnel. \nRépondez le plus honnêtement possible, la première réponse est généralement la bonne.",
                "ref": "e711018cbd3ed987",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66103546",
                            "title": "Mon travail me permet de prendre des décisions.",
                            "ref": "76fd592940bb530b",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103549",
                            "title": "Je peux exercer mon jugement pour résoudre des problèmes dans mon travail.",
                            "ref": "d8d2d559c409978b",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103637",
                            "title": "Je peux assumer des responsabilités dans mon travail.",
                            "ref": "7e9ab1310fcd22e5",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103646",
                            "title": "Au travail, je me sens libre d’exécuter mes tâches à ma façon.",
                            "ref": "170663f37280a80a",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103699",
                            "title": "J’ai les capacités pour bien faire mon travail.",
                            "ref": "0b9c143e5e7e6eb0",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103720",
                            "title": "Je me sens compétent·e à mon travail.",
                            "ref": "de90b2fb96b79653",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103829",
                            "title": "Je suis capable de résoudre des problèmes à mon travail.",
                            "ref": "bfdce0ded0f7f623",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103840",
                            "title": "Je réussis bien dans mon travail.",
                            "ref": "9f21d2b969335fb8",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103888",
                            "title": "Avec les personnes qui m’entourent dans mon milieu de travail, je me sens compris·e.",
                            "ref": "45d0204e06187721",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103892",
                            "title": "Avec les personnes qui m’entourent dans mon milieu de travail, je me sens écouté·e.",
                            "ref": "30ebba0778a4156f",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103973",
                            "title": "Avec les personnes qui m’entourent dans mon milieu de travail, je me sens en confiance.",
                            "ref": "4eea78332af969cf",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66103988",
                            "title": "Avec les personnes qui m’entourent dans mon milieu de travail, je me sens un ami pour eux.",
                            "ref": "24ad54dd60026e03",
                            "properties": {
                                "steps": 6,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Pas du tout d'accord",
                                    "right": "Tout à fait d'accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "66807517",
                "title": "*Échelle de compassion envers soi-même*\n\nLa compassion envers soi-même est la capacité à accepter ses défauts.\nEstimez si les affirmations suivantes vous correspondent. Répondez aussi franchement et spontanément que possible, ce qui compte est le vécu personnel. \n\n",
                "ref": "260f854b6164b362",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66781595",
                            "title": "J'essaie d'être compréhensif·ve et patient·e envers les aspects de ma personnalité qui me dérangent.",
                            "ref": "8bf2513265a13089",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66781598",
                            "title": "Pendant les moments très difficiles, je m'accorde la tendresse et les soins dont j'ai besoin.",
                            "ref": "a33e3dc2b4e4fbf7",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66781636",
                            "title": "Je désapprouve et critique mes propres défauts et mes insuffisances.",
                            "ref": "cf6ba2596d4d66bd",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66781675",
                            "title": "Je suis intolérant·e et impatient·e envers les aspects de ma personnalité qui me dérangent.",
                            "ref": "444daab2b9f3c6fd",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66781759",
                            "title": "Quand je me sens incompétent·e, j'essaie de me remémorer que ce sentiment est partagé par la plupart des gens.",
                            "ref": "4ec5e3102e1a7a87",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66781798",
                            "title": "J'essaie de voir mes défauts comme inhérents à la condition humaine.",
                            "ref": "2f39e2e795da3095",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67068624",
                            "title": "Lorsque j'échoue à réaliser quelque chose qui est important pour moi, j'ai tendance à me sentir seul·e dans mon échec.",
                            "ref": "7bcb937595d7322d",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66781813",
                            "title": "Lorsque je n'ai pas le moral, j'ai tendance à ressentir que la plupart des gens sont probablement plus heureux que moi.",
                            "ref": "0118d3a3de9fd83a",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66781823",
                            "title": "Lorsque quelque chose me contrarie, j'essaie de garder un équilibre émotionnel.",
                            "ref": "ab4f4d7cd0e184a4",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67068726",
                            "title": "Lorsque quelque chose de douloureux arrive, j'essaie de garder un point de vue objectif de la situation.",
                            "ref": "bfd998875f8436ce",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67068832",
                            "title": "Lorsque je n'ai pas le moral, cela m'obsède et je me focalise sur ce qui ne va pas.",
                            "ref": "50818e093e6a852b",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67068858",
                            "title": "Lorsque j'échoue à réaliser quelque chose qui est important pour moi, je suis consumé·e par un sentiment d'incompétence.",
                            "ref": "b23aa20c05fef895",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Jamais",
                                    "right": "Toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "66807687",
                "title": "*Appréciation de votre personnalité créative*\n\nLa flexibilité, l'engagement, la capacité à produire et à chercher de nouvelles idées définissent la créativité. \nRépondez le plus intuitivement possible, en prenant en compte vos habitudes sur cette dernière année. ",
                "ref": "168406a73f12fa82",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "66807816",
                            "title": "J'aime analyser un sujet en profondeur.",
                            "ref": "c5ead40a40dfedae",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66807894",
                            "title": "Je n'ai pas souvent de nouvelles idées.",
                            "ref": "6269df1a7e173087",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66808060",
                            "title": "Je suis toujours ouvert·e à de nouvelles façons de faire les choses.",
                            "ref": "46dd521891462c40",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66808071",
                            "title": "Je suis investi·e dans quasiment tout ce que je fais.",
                            "ref": "8f33a19c071b80b6",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66808115",
                            "title": "Je ne prends pas le temps d'apprendre de nouvelles choses.",
                            "ref": "585c71fb6ae68637",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66808176",
                            "title": "J'apporte souvent de nouvelles contributions.",
                            "ref": "477f0e068013e474",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66817481",
                            "title": "Je préfère me référer aux méthodes traditionnelles et validées pour faire quelque chose.",
                            "ref": "35acb47736d316e2",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66817511",
                            "title": "Je remarque rarement ce que font les autres.",
                            "ref": "70ba6e5e9e01dfc7",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66817549",
                            "title": "J'évite les opinions provoquant des conversations.",
                            "ref": "03123d60bc0bdb58",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66817563",
                            "title": "Je suis très créatif·ve.",
                            "ref": "c49be75c2427e59e",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66817626",
                            "title": "Je peux me comporter de plusieurs manières pour une situation donnée.",
                            "ref": "37bd22eff59bbdd5",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66817686",
                            "title": "Lorsque je suis confronté·e à un problème, j'essaie d'avoir une vision d'ensemble.",
                            "ref": "d98b0d81816b6b8a",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66817783",
                            "title": "Je suis très curieux·se.",
                            "ref": "5a0244f38c4d735f",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66818042",
                            "title": "J'essaie de réfléchir à de nouvelles façons de faire les choses.",
                            "ref": "f7e0318583cb853c",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66818057",
                            "title": "Je suis rarement conscient.e des changements.",
                            "ref": "6146a113a8a786c4",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66818086",
                            "title": "J'ai un esprit ouvert pour tout, même les choses qui questionnent mes croyances fondamentales.",
                            "ref": "ad9a0b8eb7b37183",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66818110",
                            "title": "J'aime être stimulé·e intellectuellement.",
                            "ref": "a5bb8377d97d6591",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66818128",
                            "title": "Je trouve facile de créer des idées nouvelles et efficaces.",
                            "ref": "e5bb6e510c48abbc",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66818176",
                            "title": "Je m'intéresse rarement à ce qui est nouveau.",
                            "ref": "5860d8f79fbec312",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66818248",
                            "title": "J'aime comprendre comment les choses fonctionnent.",
                            "ref": "34314c7737d60711",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "66818434",
                            "title": "Je ne suis pas un penseur original.",
                            "ref": "c86a1bc54ceb9e21",
                            "properties": {
                                "steps": 7,
                                "start_at_one": True,
                                "labels": {
                                    "left": "En total désaccord",
                                    "right": "En parfait accord"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            },
            {
                "id": "67054963",
                "title": "*Échelle de votre compassion envers les* *autres*\n\nLa compassion envers autrui correspond à la capacité à éprouver les sentiments et pensées des autres. \nRappelez-vous, il n'y a pas de « bonnes » ou « mauvaises » réponses, seule l'honnêteté des réponses importe. ",
                "ref": "6b3042a86733f1b8",
                "properties": {
                    "show_button": False,
                    "button_text": "Continuer",
                    "fields": [
                        {
                            "id": "67055227",
                            "title": "Lorsque d’autres personnes pleurent autour de moi, je ne ressens presque rien.",
                            "ref": "090ec9cabcbb7145",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055264",
                            "title": "Parfois, lorsque les gens me parlent de leur problème, j’ai des difficultés à me sentir concerné·e.",
                            "ref": "d8f542084f4325b6",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055301",
                            "title": "Je ne me sens pas émotionnellement connecté·e aux personnes qui souffrent.",
                            "ref": "93aeb7555813eec6",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055300",
                            "title": "Je suis attentif·ve lorsque d’autres personnes me parlent.",
                            "ref": "c295360636ad5702",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055298",
                            "title": "Je me sens détaché·e lorsque les autres me racontent leur malheur.",
                            "ref": "defe99f8dc0dd013",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055297",
                            "title": "Lorsqu’une personne traverse une période difficile, j’essaie de faire attention à elle.",
                            "ref": "a78050b45f15f265",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055296",
                            "title": "Je fais la sourde oreille lorsqu’on me parle de ses problèmes.",
                            "ref": "0a2ad38b004563bf",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055294",
                            "title": "J’aime être présent·e pour les autres dans les moments difficiles.",
                            "ref": "f6b45f645aa2cb08",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055293",
                            "title": "Même s’ils ne disent rien, je remarque lorsque les gens sont contrariés.",
                            "ref": "b34182bdf55e1bd6",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055291",
                            "title": "Lorsque je vois quelqu’un de déprimé, je sens que je ne peux pas m’identifier à lui.",
                            "ref": "adc9c4c0026d4947",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055290",
                            "title": "Tout le monde peut se sentir déprimé par moment, cela fait partie de l’être humain.",
                            "ref": "856c963c821d8141",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67181128",
                            "title": "Parfois, je suis froid·e avec les personnes qui ne se sentent pas bien.",
                            "ref": "e5997fe1650ea62d",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055288",
                            "title": "J’essaie d’écouter patiemment lorsque que les gens me racontent leurs problèmes.",
                            "ref": "00b4eb32ff942afb",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055285",
                            "title": "Je ne me préoccupe pas des problèmes des autres.",
                            "ref": "1f18cc0040a9f2c6",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055283",
                            "title": "Il est important de reconnaître que les individus ont des faiblesses et que personne n’est parfait.",
                            "ref": "f1373b3e4f7ab053",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055915",
                            "title": "Mon cœur se tourne vers ceux qui sont malheureux.",
                            "ref": "08cd4b578a8982ef",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055914",
                            "title": "Malgré mes différences avec les autres, je sais que tout le monde ressent de la douleur tout comme moi.",
                            "ref": "e72fcd5558aeafff",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055913",
                            "title": "Quand les autres se sentent troublés, je laisse habituellement quelqu'un d'autre s'occuper d'eux.",
                            "ref": "8c83d4ff4f2ab889",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055912",
                            "title": "Je ne pense pas beaucoup aux préoccupations des autres.",
                            "ref": "075d6c30167391d9",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055911",
                            "title": "La souffrance est juste une partie de l’expérience humaine.",
                            "ref": "8cb30ebd730b45ff",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055909",
                            "title": "Lorsque les autres me parlent de leurs problèmes, j’ai tendance à garder une vision objective de la situation.",
                            "ref": "01a4840b41241b19",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055908",
                            "title": "Je ne peux pas vraiment me relier aux personnes qui souffrent.",
                            "ref": "587a8c2f5c7ebc59",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055905",
                            "title": "Je tends à éviter les personnes qui éprouvent beaucoup de souffrance.",
                            "ref": "344a58e6befb8c99",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        },
                        {
                            "id": "67055904",
                            "title": "J’essaie de réconforter les autres lorsqu’ils se sentent tristes.",
                            "ref": "d8776b0cb605c5f5",
                            "properties": {
                                "steps": 5,
                                "start_at_one": True,
                                "labels": {
                                    "left": "Presque jamais",
                                    "center": "Neutre",
                                    "right": "Presque toujours"
                                }
                            },
                            "validations": {
                                "required": True
                            },
                            "type": "opinion_scale"
                        }
                    ]
                },
                "type": "group"
            }
        ],
        "hidden": [
            "id"
        ],
        "logic": [
            {
                "type": "field",
                "ref": "1d8ce68058a078d3",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d8ce68058a078d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d8ce68058a078d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d8ce68058a078d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d8ce68058a078d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d8ce68058a078d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d8ce68058a078d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "ae23abd0fadb2fd4",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ae23abd0fadb2fd4"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ae23abd0fadb2fd4"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ae23abd0fadb2fd4"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ae23abd0fadb2fd4"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ae23abd0fadb2fd4"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ae23abd0fadb2fd4"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "a36f63651817f271",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a36f63651817f271"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a36f63651817f271"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a36f63651817f271"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a36f63651817f271"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a36f63651817f271"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a36f63651817f271"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "b7427ccd4109eba1",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b7427ccd4109eba1"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b7427ccd4109eba1"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b7427ccd4109eba1"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b7427ccd4109eba1"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b7427ccd4109eba1"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b7427ccd4109eba1"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "5a61eeef16a97901",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a61eeef16a97901"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a61eeef16a97901"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a61eeef16a97901"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a61eeef16a97901"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a61eeef16a97901"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a61eeef16a97901"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "d58dc085db4d72a8",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d58dc085db4d72a8"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d58dc085db4d72a8"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d58dc085db4d72a8"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d58dc085db4d72a8"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d58dc085db4d72a8"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d58dc085db4d72a8"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "1d46638bbe5fca1d",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d46638bbe5fca1d"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d46638bbe5fca1d"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d46638bbe5fca1d"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d46638bbe5fca1d"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d46638bbe5fca1d"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1d46638bbe5fca1d"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "8a4d91380b080a46",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "8a4d91380b080a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "8a4d91380b080a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "8a4d91380b080a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "8a4d91380b080a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "8a4d91380b080a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "8a4d91380b080a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "d86bd5e2b324b2c3",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d86bd5e2b324b2c3"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d86bd5e2b324b2c3"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d86bd5e2b324b2c3"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d86bd5e2b324b2c3"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d86bd5e2b324b2c3"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d86bd5e2b324b2c3"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "4d3870f4272feff3",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4d3870f4272feff3"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4d3870f4272feff3"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4d3870f4272feff3"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4d3870f4272feff3"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4d3870f4272feff3"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4d3870f4272feff3"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "d88d380837d6bbf5",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d88d380837d6bbf5"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d88d380837d6bbf5"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d88d380837d6bbf5"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d88d380837d6bbf5"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d88d380837d6bbf5"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d88d380837d6bbf5"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "d139814355bc5597",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d139814355bc5597"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d139814355bc5597"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d139814355bc5597"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d139814355bc5597"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d139814355bc5597"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "d139814355bc5597"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "888bd7dbeb46c2eb",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "888bd7dbeb46c2eb"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "888bd7dbeb46c2eb"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "888bd7dbeb46c2eb"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "888bd7dbeb46c2eb"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "888bd7dbeb46c2eb"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "888bd7dbeb46c2eb"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "60045398d33c1e8f",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "60045398d33c1e8f"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "60045398d33c1e8f"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "60045398d33c1e8f"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "60045398d33c1e8f"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "60045398d33c1e8f"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "60045398d33c1e8f"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "54fd8613d60edfe9",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "54fd8613d60edfe9"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "54fd8613d60edfe9"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "54fd8613d60edfe9"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "54fd8613d60edfe9"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "54fd8613d60edfe9"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "54fd8613d60edfe9"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "4b0eaa2d02d45103",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4b0eaa2d02d45103"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4b0eaa2d02d45103"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4b0eaa2d02d45103"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4b0eaa2d02d45103"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4b0eaa2d02d45103"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4b0eaa2d02d45103"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "5a2a7cb43d2f6982",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a2a7cb43d2f6982"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a2a7cb43d2f6982"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a2a7cb43d2f6982"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a2a7cb43d2f6982"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a2a7cb43d2f6982"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "5a2a7cb43d2f6982"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "1b67640780d61d1a",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b67640780d61d1a"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b67640780d61d1a"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b67640780d61d1a"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b67640780d61d1a"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b67640780d61d1a"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b67640780d61d1a"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "ff6698e23d7142f9",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ff6698e23d7142f9"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ff6698e23d7142f9"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ff6698e23d7142f9"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ff6698e23d7142f9"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ff6698e23d7142f9"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ff6698e23d7142f9"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "7c7bf5718c0e56a1",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "7c7bf5718c0e56a1"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "7c7bf5718c0e56a1"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "7c7bf5718c0e56a1"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "7c7bf5718c0e56a1"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "7c7bf5718c0e56a1"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "7c7bf5718c0e56a1"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "4ebccff60492ecb6",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4ebccff60492ecb6"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4ebccff60492ecb6"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4ebccff60492ecb6"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4ebccff60492ecb6"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4ebccff60492ecb6"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "4ebccff60492ecb6"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "c4246197bf464a46",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c4246197bf464a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c4246197bf464a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c4246197bf464a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c4246197bf464a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c4246197bf464a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c4246197bf464a46"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "9ff67fc7902a9d3d",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ff67fc7902a9d3d"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ff67fc7902a9d3d"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ff67fc7902a9d3d"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ff67fc7902a9d3d"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ff67fc7902a9d3d"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ff67fc7902a9d3d"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "3600db47fdaf4ac4",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "3600db47fdaf4ac4"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "3600db47fdaf4ac4"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "3600db47fdaf4ac4"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "3600db47fdaf4ac4"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "3600db47fdaf4ac4"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "3600db47fdaf4ac4"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "592492ad2b595c35",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "592492ad2b595c35"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "592492ad2b595c35"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "592492ad2b595c35"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "592492ad2b595c35"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "592492ad2b595c35"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "592492ad2b595c35"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "93d8431cf45383fc",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "93d8431cf45383fc"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "93d8431cf45383fc"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "93d8431cf45383fc"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "93d8431cf45383fc"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "93d8431cf45383fc"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "93d8431cf45383fc"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "b2976004bac37d0a",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b2976004bac37d0a"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b2976004bac37d0a"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b2976004bac37d0a"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b2976004bac37d0a"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b2976004bac37d0a"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b2976004bac37d0a"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "ebff4306c942b5d3",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ebff4306c942b5d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ebff4306c942b5d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ebff4306c942b5d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ebff4306c942b5d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ebff4306c942b5d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "ebff4306c942b5d3"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "cc20ba7ee8236fc2",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "cc20ba7ee8236fc2"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "cc20ba7ee8236fc2"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "cc20ba7ee8236fc2"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "cc20ba7ee8236fc2"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "cc20ba7ee8236fc2"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "cc20ba7ee8236fc2"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "f4d3c0c50464bfa3",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f4d3c0c50464bfa3"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f4d3c0c50464bfa3"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f4d3c0c50464bfa3"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f4d3c0c50464bfa3"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f4d3c0c50464bfa3"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f4d3c0c50464bfa3"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "c8657efc77f76b21",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c8657efc77f76b21"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c8657efc77f76b21"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c8657efc77f76b21"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c8657efc77f76b21"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c8657efc77f76b21"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "c8657efc77f76b21"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "1340b50e9d8b7fcb",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1340b50e9d8b7fcb"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1340b50e9d8b7fcb"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1340b50e9d8b7fcb"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1340b50e9d8b7fcb"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1340b50e9d8b7fcb"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1340b50e9d8b7fcb"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "011785d4e1de2136",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "011785d4e1de2136"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "011785d4e1de2136"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "011785d4e1de2136"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "011785d4e1de2136"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "011785d4e1de2136"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "011785d4e1de2136"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "88d7c718663903fa",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "88d7c718663903fa"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "88d7c718663903fa"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "88d7c718663903fa"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "88d7c718663903fa"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "88d7c718663903fa"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "88d7c718663903fa"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "b95f80c57a8d361b",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b95f80c57a8d361b"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b95f80c57a8d361b"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b95f80c57a8d361b"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b95f80c57a8d361b"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b95f80c57a8d361b"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "b95f80c57a8d361b"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "f182e0833fa433db",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f182e0833fa433db"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f182e0833fa433db"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f182e0833fa433db"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f182e0833fa433db"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f182e0833fa433db"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "f182e0833fa433db"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "1b8d806e719ff8fd",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b8d806e719ff8fd"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b8d806e719ff8fd"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b8d806e719ff8fd"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b8d806e719ff8fd"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b8d806e719ff8fd"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "1b8d806e719ff8fd"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "95a5ecf5133a46a2",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "95a5ecf5133a46a2"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "95a5ecf5133a46a2"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "95a5ecf5133a46a2"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "95a5ecf5133a46a2"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "95a5ecf5133a46a2"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "95a5ecf5133a46a2"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "9ea0241175a177e8",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ea0241175a177e8"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ea0241175a177e8"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ea0241175a177e8"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ea0241175a177e8"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ea0241175a177e8"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "9ea0241175a177e8"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "e1bb383ebd4f79ce",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e1bb383ebd4f79ce"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e1bb383ebd4f79ce"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e1bb383ebd4f79ce"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e1bb383ebd4f79ce"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e1bb383ebd4f79ce"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e1bb383ebd4f79ce"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "aa1a88e424a1c318",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "aa1a88e424a1c318"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "aa1a88e424a1c318"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "aa1a88e424a1c318"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "aa1a88e424a1c318"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "aa1a88e424a1c318"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "aa1a88e424a1c318"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "e4fe610efee0c030",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e4fe610efee0c030"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e4fe610efee0c030"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e4fe610efee0c030"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e4fe610efee0c030"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e4fe610efee0c030"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "e4fe610efee0c030"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "fb0450729e0be62c",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "fb0450729e0be62c"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "fb0450729e0be62c"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "fb0450729e0be62c"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "fb0450729e0be62c"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "fb0450729e0be62c"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "fb0450729e0be62c"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "field",
                "ref": "a7972bfcb8a9c0cd",
                "actions": [
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 6
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a7972bfcb8a9c0cd"
                                },
                                {
                                    "type": "constant",
                                    "value": 1
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 5
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a7972bfcb8a9c0cd"
                                },
                                {
                                    "type": "constant",
                                    "value": 2
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 4
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a7972bfcb8a9c0cd"
                                },
                                {
                                    "type": "constant",
                                    "value": 3
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 3
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a7972bfcb8a9c0cd"
                                },
                                {
                                    "type": "constant",
                                    "value": 4
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 2
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a7972bfcb8a9c0cd"
                                },
                                {
                                    "type": "constant",
                                    "value": 5
                                }
                            ]
                        }
                    },
                    {
                        "action": "add",
                        "details": {
                            "target": {
                                "type": "variable",
                                "value": "score"
                            },
                            "value": {
                                "type": "constant",
                                "value": 1
                            }
                        },
                        "condition": {
                            "op": "equal",
                            "vars": [
                                {
                                    "type": "field",
                                    "value": "a7972bfcb8a9c0cd"
                                },
                                {
                                    "type": "constant",
                                    "value": 6
                                }
                            ]
                        }
                    }
                ]
            }
        ],
        "variables": {
            "score": 0
        },
        "_links": {
            "display": "https://omind.typeform.com/to/HoS3mL"
        }
    }
    return form


@pytest.fixture(scope='function')
def vr_response():
    response = {
        "answers": [
            {
                "field": {
                    "id": "66689526",
                    "ref": "eb62a550b68d93d4",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66690416",
                    "ref": "780b7ea2c140bd78",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103888",
                    "ref": "45d0204e06187721",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710142",
                    "ref": "60cbf91a434603cd",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777471",
                    "ref": "4d3870f4272feff3",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66808071",
                    "ref": "8f33a19c071b80b6",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "choice": {
                    "label": "2-3 fois par semaine"
                },
                "field": {
                    "id": "66708596",
                    "ref": "057b82c2e4dde124",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66777750",
                    "ref": "5a2a7cb43d2f6982",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711202",
                    "ref": "b769244e862847d4",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707208",
                    "ref": "9699bcee2f3f7d30",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707686",
                    "ref": "95d9964ad2a9d7e0",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710171",
                    "ref": "9dd6e1c81d654a0b",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711085",
                    "ref": "fe5812e40d89ae9b",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778541",
                    "ref": "c8657efc77f76b21",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66689694",
                    "ref": "265df217b391e127",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711058",
                    "ref": "d721d8e2e1c1d42d",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777595",
                    "ref": "888bd7dbeb46c2eb",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055264",
                    "ref": "d8f542084f4325b6",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66818110",
                    "ref": "a5bb8377d97d6591",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055294",
                    "ref": "f6b45f645aa2cb08",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777712",
                    "ref": "60045398d33c1e8f",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707134",
                    "ref": "aed5a9ea2ae59960",
                    "type": "opinion_scale"
                },
                "number": 1,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055905",
                    "ref": "344a58e6befb8c99",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103829",
                    "ref": "bfdce0ded0f7f623",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777737",
                    "ref": "4b0eaa2d02d45103",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778681",
                    "ref": "1b8d806e719ff8fd",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66781595",
                    "ref": "8bf2513265a13089",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714210",
                    "ref": "ae23abd0fadb2fd4",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707833",
                    "ref": "c381c5a1615b0352",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711104",
                    "ref": "94ea24871d07e14f",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777888",
                    "ref": "7c7bf5718c0e56a1",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "choice": {
                    "label": "1 fois par semaine"
                },
                "field": {
                    "id": "66708624",
                    "ref": "c618a05dcef23bca",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66690495",
                    "ref": "7c52a051dd1fdf20",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777852",
                    "ref": "ff6698e23d7142f9",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "choice": {
                    "label": "Homme"
                },
                "field": {
                    "id": "66527781",
                    "ref": "c1a31ab9186c2ffc",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "67068624",
                    "ref": "7bcb937595d7322d",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778155",
                    "ref": "592492ad2b595c35",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778756",
                    "ref": "aa1a88e424a1c318",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778890",
                    "ref": "a7972bfcb8a9c0cd",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66817549",
                    "ref": "03123d60bc0bdb58",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711012",
                    "ref": "e59f6eeb559662d8",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714315",
                    "ref": "394a9832ae171c98",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714502",
                    "ref": "85fcad1084061923",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714619",
                    "ref": "40d43195d5f5a139",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710935",
                    "ref": "0cace96ac90577b7",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778614",
                    "ref": "b95f80c57a8d361b",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707697",
                    "ref": "3e2b29a8d17fe93c",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "choice": {
                    "label": "1 \u00e0 2 fois"
                },
                "field": {
                    "id": "66709064",
                    "ref": "848768bf553ff5e7",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66777556",
                    "ref": "d88d380837d6bbf5",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778132",
                    "ref": "3600db47fdaf4ac4",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "67028424",
                    "ref": "42b72c68f027f50c",
                    "type": "long_text"
                },
                "text": "Rien de sp\u00e9cial je suis curieux ;)",
                "type": "text"
            },
            {
                "field": {
                    "id": "66103840",
                    "ref": "9f21d2b969335fb8",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707704",
                    "ref": "d7fb68d48239b52c",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711187",
                    "ref": "ae3ca7cd9cd16b33",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714158",
                    "ref": "66cb1a6b8f6354aa",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66808176",
                    "ref": "477f0e068013e474",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778592",
                    "ref": "88d7c718663903fa",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710253",
                    "ref": "f6fa185b6f7355f3",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777453",
                    "ref": "d86bd5e2b324b2c3",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "choice": {
                    "label": "2-3 fois par semaine"
                },
                "field": {
                    "id": "66708523",
                    "ref": "f109c3f45764ab61",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66689676",
                    "ref": "9afcdc6328efc5d2",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707951",
                    "ref": "ded59d4c4e2c96d4",
                    "type": "opinion_scale"
                },
                "number": 1,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710364",
                    "ref": "c724a3de7c82ff58",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710570",
                    "ref": "07fb194f7f8de09e",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "choice": {
                    "label": "2-3 fois par semaine"
                },
                "field": {
                    "id": "66708326",
                    "ref": "7758bec371913adb",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "67055285",
                    "ref": "1f18cc0040a9f2c6",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055908",
                    "ref": "587a8c2f5c7ebc59",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707264",
                    "ref": "ca77ccd1f7aaad41",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778332",
                    "ref": "cc20ba7ee8236fc2",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055227",
                    "ref": "090ec9cabcbb7145",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707251",
                    "ref": "5eca865c9ed63399",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710038",
                    "ref": "9496c04b091aa795",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711230",
                    "ref": "8891ce7bdaedbf21",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66689254",
                    "ref": "b9ce88e88c7107d2",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778646",
                    "ref": "f182e0833fa433db",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103546",
                    "ref": "76fd592940bb530b",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707787",
                    "ref": "90f442db38ee6549",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714715",
                    "ref": "a36f63651817f271",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777041",
                    "ref": "5a61eeef16a97901",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707066",
                    "ref": "722835a0549afd5d",
                    "type": "opinion_scale"
                },
                "number": 1,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778700",
                    "ref": "9ea0241175a177e8",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710225",
                    "ref": "91a446a9af8cb1a7",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777843",
                    "ref": "1b67640780d61d1a",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778586",
                    "ref": "011785d4e1de2136",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66781823",
                    "ref": "ab4f4d7cd0e184a4",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710041",
                    "ref": "87357f7f3121acec",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707088",
                    "ref": "71cd4395aad46376",
                    "type": "opinion_scale"
                },
                "number": 1,
                "type": "number"
            },
            {
                "field": {
                    "id": "67181128",
                    "ref": "e5997fe1650ea62d",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "choice": {
                    "label": "Presque tous les jours"
                },
                "field": {
                    "id": "66709006",
                    "ref": "610255b27d463cb0",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66777593",
                    "ref": "d139814355bc5597",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "67068832",
                    "ref": "50818e093e6a852b",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711130",
                    "ref": "f81d8ef23e1709f0",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66708177",
                    "ref": "bbeb4c23008f2eff",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711048",
                    "ref": "68c1d595fe936ae6",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "choice": {
                    "label": "Presque tous les jours"
                },
                "field": {
                    "id": "66687419",
                    "ref": "47373e16dfeb7d01",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66707926",
                    "ref": "240a501c576c0df8",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778692",
                    "ref": "95a5ecf5133a46a2",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "choice": {
                    "label": "1 fois par semaine"
                },
                "field": {
                    "id": "66708558",
                    "ref": "3c22d6b5c5394e79",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66714138",
                    "ref": "9abf2704be10509d",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714637",
                    "ref": "b7427ccd4109eba1",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778316",
                    "ref": "ebff4306c942b5d3",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778530",
                    "ref": "f4d3c0c50464bfa3",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055904",
                    "ref": "d8776b0cb605c5f5",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "67064375",
                    "ref": "0f2b1cc7eb53d5d7",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778842",
                    "ref": "e4fe610efee0c030",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66817481",
                    "ref": "35acb47736d316e2",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778196",
                    "ref": "b2976004bac37d0a",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66808115",
                    "ref": "585c71fb6ae68637",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66818248",
                    "ref": "34314c7737d60711",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103892",
                    "ref": "30ebba0778a4156f",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103988",
                    "ref": "24ad54dd60026e03",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "choice": {
                    "label": "Presque tous les jours"
                },
                "field": {
                    "id": "66708289",
                    "ref": "e53f0bc7317e6995",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66817511",
                    "ref": "70ba6e5e9e01dfc7",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055914",
                    "ref": "e72fcd5558aeafff",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103549",
                    "ref": "d8d2d559c409978b",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "choice": {
                    "label": "2-3 fois par semaine"
                },
                "field": {
                    "id": "66708898",
                    "ref": "1a02f69d82bd2b31",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66103973",
                    "ref": "4eea78332af969cf",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711240",
                    "ref": "69a215b415a6ac64",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66818057",
                    "ref": "6146a113a8a786c4",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055301",
                    "ref": "93aeb7555813eec6",
                    "type": "opinion_scale"
                },
                "number": 1,
                "type": "number"
            },
            {
                "boolean": True,
                "field": {
                    "id": "66524670",
                    "ref": "1b1d64b702825f3f",
                    "type": "legal"
                },
                "type": "boolean"
            },
            {
                "field": {
                    "id": "66706984",
                    "ref": "6be3d6ad406dcb8e",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710194",
                    "ref": "8de24a09fb5f931e",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710349",
                    "ref": "a99f2714a424d7d2",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777446",
                    "ref": "8a4d91380b080a46",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707039",
                    "ref": "c9328836454bd690",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055298",
                    "ref": "defe99f8dc0dd013",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66708170",
                    "ref": "ecb9d1b076f99507",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714105",
                    "ref": "7879757020cd9c81",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66808060",
                    "ref": "46dd521891462c40",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66689501",
                    "ref": "2c36984e35e9b620",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710957",
                    "ref": "2513d19ea3ea55e6",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66713510",
                    "ref": "5cf1e55be91c0074",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055293",
                    "ref": "b34182bdf55e1bd6",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "67068858",
                    "ref": "b23aa20c05fef895",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707850",
                    "ref": "724da58bdf243133",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66781675",
                    "ref": "444daab2b9f3c6fd",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66818042",
                    "ref": "f7e0318583cb853c",
                    "type": "opinion_scale"
                },
                "number": 7,
                "type": "number"
            },
            {
                "field": {
                    "id": "66818128",
                    "ref": "e5bb6e510c48abbc",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055912",
                    "ref": "075d6c30167391d9",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707126",
                    "ref": "0ed3437ad95761db",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055915",
                    "ref": "08cd4b578a8982ef",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "choice": {
                    "label": "2-3 fois par semaine"
                },
                "field": {
                    "id": "66708834",
                    "ref": "3a66917386b1afeb",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66103699",
                    "ref": "0b9c143e5e7e6eb0",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707763",
                    "ref": "36ca651340f7ceab",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710279",
                    "ref": "202f8f9d5e4f4d3b",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714335",
                    "ref": "5431184ea56f0860",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055291",
                    "ref": "adc9c4c0026d4947",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055290",
                    "ref": "856c963c821d8141",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707659",
                    "ref": "9d1d1e49966ff86f",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778039",
                    "ref": "9ff67fc7902a9d3d",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055913",
                    "ref": "8c83d4ff4f2ab889",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710207",
                    "ref": "9ffd7add81988348",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707779",
                    "ref": "eab3e5693041f64b",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707959",
                    "ref": "62e5ea4cbd186476",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055909",
                    "ref": "01a4840b41241b19",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66818434",
                    "ref": "c86a1bc54ceb9e21",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707057",
                    "ref": "993ecdfd0c9a5ec4",
                    "type": "opinion_scale"
                },
                "number": 1,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707656",
                    "ref": "9c468c7266fd3c94",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66713942",
                    "ref": "704c4e5cad5525dc",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103637",
                    "ref": "7e9ab1310fcd22e5",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055911",
                    "ref": "8cb30ebd730b45ff",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66713525",
                    "ref": "1d8ce68058a078d3",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055300",
                    "ref": "c295360636ad5702",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710102",
                    "ref": "fce9ad6e96ebad69",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714119",
                    "ref": "5d20ba1aa92bab1a",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777955",
                    "ref": "4ebccff60492ecb6",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66817783",
                    "ref": "5a0244f38c4d735f",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778171",
                    "ref": "93d8431cf45383fc",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66708154",
                    "ref": "72bf007ebdd079b3",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777998",
                    "ref": "c4246197bf464a46",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66781636",
                    "ref": "cf6ba2596d4d66bd",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66781759",
                    "ref": "4ec5e3102e1a7a87",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103646",
                    "ref": "170663f37280a80a",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055288",
                    "ref": "00b4eb32ff942afb",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66817626",
                    "ref": "37bd22eff59bbdd5",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710564",
                    "ref": "3cdaede9cb0dcb10",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66714059",
                    "ref": "a0f7963885491790",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66710558",
                    "ref": "7f9f956e8f499134",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66689847",
                    "ref": "ac27f42869d120a2",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66807816",
                    "ref": "c5ead40a40dfedae",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66818086",
                    "ref": "ad9a0b8eb7b37183",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66689708",
                    "ref": "e35d48c3a5f5c45e",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66817686",
                    "ref": "d98b0d81816b6b8a",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778557",
                    "ref": "1340b50e9d8b7fcb",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "67068726",
                    "ref": "bfd998875f8436ce",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777438",
                    "ref": "1d46638bbe5fca1d",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66689224",
                    "ref": "08e0aab3c025aa19",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777261",
                    "ref": "d58dc085db4d72a8",
                    "type": "opinion_scale"
                },
                "number": 6,
                "type": "number"
            },
            {
                "field": {
                    "id": "66528769",
                    "ref": "d5406020e2e8ac23",
                    "type": "number"
                },
                "number": 1982,
                "type": "number"
            },
            {
                "choice": {
                    "label": "2-3 fois par semaine"
                },
                "field": {
                    "id": "66708927",
                    "ref": "ef1cf5df16810419",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66708066",
                    "ref": "a5e5a047faf6f879",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66807894",
                    "ref": "6269df1a7e173087",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055283",
                    "ref": "f1373b3e4f7ab053",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "choice": {
                    "label": "Presque tous les jours"
                },
                "field": {
                    "id": "66708446",
                    "ref": "ddc572070aeec689",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66778855",
                    "ref": "fb0450729e0be62c",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707103",
                    "ref": "cdf035e91c187449",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66781798",
                    "ref": "2f39e2e795da3095",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055297",
                    "ref": "a78050b45f15f265",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707898",
                    "ref": "9e73c953b3a923be",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66707186",
                    "ref": "3a4203f0b22df1ea",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66781598",
                    "ref": "a33e3dc2b4e4fbf7",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66817563",
                    "ref": "c49be75c2427e59e",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "field": {
                    "id": "66818176",
                    "ref": "5860d8f79fbec312",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66711274",
                    "ref": "5da1d6341893121a",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66777730",
                    "ref": "54fd8613d60edfe9",
                    "type": "opinion_scale"
                },
                "number": 5,
                "type": "number"
            },
            {
                "field": {
                    "id": "66781813",
                    "ref": "0118d3a3de9fd83a",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "67055296",
                    "ref": "0a2ad38b004563bf",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66103720",
                    "ref": "de90b2fb96b79653",
                    "type": "opinion_scale"
                },
                "number": 4,
                "type": "number"
            },
            {
                "choice": {
                    "label": "1 \u00e0 2 fois"
                },
                "field": {
                    "id": "66708352",
                    "ref": "3e01e3861f317b64",
                    "type": "multiple_choice"
                },
                "type": "choice"
            },
            {
                "field": {
                    "id": "66710259",
                    "ref": "23565be5165e274d",
                    "type": "opinion_scale"
                },
                "number": 2,
                "type": "number"
            },
            {
                "field": {
                    "id": "66778745",
                    "ref": "e1bb383ebd4f79ce",
                    "type": "opinion_scale"
                },
                "number": 3,
                "type": "number"
            }
        ],
        "calculated": {
            "score": 124
        },
        "hidden": {
            "id": "unit-test-fake-user-hash"
        },
        "landed_at": "2018-11-10T16:01:06Z",
        "landing_id": "748e9880-6aa1-11ea-bda8-5f255b527162",  # anonymized
        "metadata": {
            "browser": "default",
            "network_id": "830a26cb1a",
            "platform": "other",
            "referer": "https://omind.typeform.com/to/HoS3mL?id=unit-test-fake-user-hash",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
        },
        "response_id": "748e9880-6aa1-11ea-bda8-5f255b527162",  # anonymized
        "submitted_at": "2018-11-10T16:33:33Z",
        "token": "748e9880-6aa1-11ea-bda8-5f255b527162",  # anonymized
        "variables": [
            {
                "key": "score",
                "number": 124,
                "type": "number"
            }
        ]
    }
    return response
