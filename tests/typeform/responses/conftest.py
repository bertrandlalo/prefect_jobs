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
