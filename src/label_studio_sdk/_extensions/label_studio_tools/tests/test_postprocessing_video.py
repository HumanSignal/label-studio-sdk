from label_studio_tools.postprocessing.video import extract_key_frames


def test_video_disabled_till_end():
    """
    Test frames extraction with disabled in the end and frame count > disabled key frame
    """
    example = [
        {
            "id": "tJhYZLMC9G",
            "type": "videorectangle",
            "value": {
                "labels": ["Airplane"],
                "framesCount": 10000000,
                "sequence": [
                    {
                        "frame": 1,
                        "enabled": True,
                        "x": 38,
                        "y": 38,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 1.22,
                    },
                    {
                        "frame": 5,
                        "enabled": False,
                        "x": 40,
                        "y": 49,
                        "width": 56,
                        "height": 34,
                        "rotation": 30,
                        "time": 3.44,
                    },
                ],
                "from_name": "test",
            },
        }
    ]
    key_frames = extract_key_frames(example)
    assert len(key_frames[0]['value']['sequence']) == 5
    key_frames = key_frames[0]['value']['sequence']
    assert key_frames[0]['x'] == 38
    assert key_frames[0]['y'] == 38
    assert key_frames[0]['width'] == 41
    assert key_frames[0]['height'] == 22
    assert key_frames[0]['rotation'] == 0
    assert key_frames[0]['time'] == 1.22
    assert key_frames[4]['x'] == 40
    assert key_frames[4]['y'] == 49
    assert key_frames[4]['width'] == 56
    assert key_frames[4]['height'] == 34
    assert key_frames[4]['rotation'] == 30
    assert key_frames[4]['time'] == 3.44
    assert key_frames[2]['x'] == 39
    assert key_frames[2]['y'] == 43.5
    assert key_frames[2]['width'] == 48.5
    assert key_frames[2]['height'] == 28
    assert key_frames[2]['rotation'] == 15
    assert key_frames[2]['auto']
    assert key_frames[2]['time'] == 2.33
    assert not key_frames[0].get('auto')
    assert not key_frames[4].get('auto')


def test_video_enabled_till_end():
    """
    Test frames extraction with enabled in the end and frame count > enabled key frame
    """
    example = [
        {
            "id": "tJhYZLMC9G",
            "type": "videorectangle",
            "value": {
                "labels": ["Airplane"],
                "framesCount": 10,
                "duration": 10.10,
                "sequence": [
                    {
                        "frame": 1,
                        "enabled": True,
                        "x": 38,
                        "y": 38,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 1.01,
                    },
                    {
                        "frame": 5,
                        "enabled": True,
                        "x": 40,
                        "y": 49,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 5.05,
                    },
                ],
            },
        }
    ]
    key_frames = extract_key_frames(example)[0]['value']['sequence']
    assert len(key_frames) == 10
    assert key_frames[0]['x'] == 38
    assert key_frames[0]['y'] == 38
    assert key_frames[0]['width'] == 41
    assert key_frames[0]['height'] == 22
    assert key_frames[0]['rotation'] == 0
    assert key_frames[0]['time'] == 1.01
    assert key_frames[4]['x'] == 40
    assert key_frames[4]['y'] == 49
    assert key_frames[4]['width'] == 41
    assert key_frames[4]['height'] == 22
    assert key_frames[4]['rotation'] == 0
    assert key_frames[4]['time'] == 5.05
    assert key_frames[2]['x'] == 39
    assert key_frames[2]['y'] == 43.5
    assert key_frames[2]['width'] == 41
    assert key_frames[2]['height'] == 22
    assert key_frames[2]['rotation'] == 0
    assert key_frames[2]['auto']
    assert key_frames[2]['time'] == 3.03
    assert not key_frames[0].get('auto')
    assert not key_frames[4].get('auto')
    assert key_frames[5]['x'] == 40
    assert key_frames[5]['y'] == 49
    assert key_frames[5]['width'] == 41
    assert key_frames[5]['height'] == 22
    assert key_frames[5]['rotation'] == 0
    assert key_frames[5].get('auto')
    assert key_frames[8]['x'] == 40
    assert key_frames[8]['y'] == 49
    assert key_frames[8]['width'] == 41
    assert key_frames[8]['height'] == 22
    assert key_frames[8]['rotation'] == 0
    assert key_frames[8]['auto']
    assert key_frames[9]['x'] == 40
    assert key_frames[9]['y'] == 49
    assert key_frames[9]['width'] == 41
    assert key_frames[9]['height'] == 22
    assert key_frames[9]['rotation'] == 0
    assert key_frames[9]['time'] == 10.10
    assert key_frames[9].get('auto')


def test_video_enabled_till_end_one_frame():
    """
    Test frames extraction with enabled in the end and frame count > enabled key frame
    """
    example = [
        {
            "id": "tJhYZLMC9G",
            "type": "videorectangle",
            "value": {
                "labels": ["Airplane", "Test"],
                "framesCount": 10,
                "duration": 9,
                "sequence": [
                    {
                        "frame": 1,
                        "enabled": True,
                        "x": 38,
                        "y": 38,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 1,
                    }
                ],
            },
        }
    ]
    key_frames = extract_key_frames(example)[0]['value']['sequence']
    assert len(key_frames) == 10
    assert key_frames[0]['x'] == 38
    assert key_frames[0]['y'] == 38
    assert key_frames[0]['width'] == 41
    assert key_frames[0]['height'] == 22
    assert key_frames[0]['rotation'] == 0
    assert key_frames[0]['time'] == 1
    assert key_frames[9]['x'] == 38
    assert key_frames[9]['y'] == 38
    assert key_frames[9]['width'] == 41
    assert key_frames[9]['height'] == 22
    assert key_frames[9]['rotation'] == 0
    assert key_frames[9]['time'] == 9
    assert key_frames[9]['auto']


def test_video_disabled_till_end_one_frame():
    """
    Test frames extraction with disabled in the end and frame count > enabled key frame
    """
    example = [
        {
            "id": "tJhYZLMC9G",
            "type": "videorectangle",
            "value": {
                "labels": ["Airplane"],
                "framesCount": 10,
                "sequence": [
                    {
                        "frame": 1,
                        "enabled": False,
                        "x": 38,
                        "y": 38,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                    }
                ],
            },
        }
    ]
    key_frames = extract_key_frames(example)[0]['value']['sequence']
    assert len(key_frames) == 1


def test_video_disabled_till_end_keyframe_count():
    """
    Test frames extraction with disabled in the end and frame count > disabled key frame
    """
    example = [
        {
            "id": "tJhYZLMC9G",
            "type": "videorectangle",
            "value": {
                "labels": ["Airplane"],
                "framesCount": 10000000,
                "duration": 22,
                "sequence": [
                    {
                        "frame": 1,
                        "enabled": True,
                        "x": 38,
                        "y": 38,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 1,
                    },
                    {
                        "frame": 5,
                        "enabled": False,
                        "x": 40,
                        "y": 49,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 5,
                    },
                    {
                        "frame": 11,
                        "enabled": True,
                        "x": 38,
                        "y": 38,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 11,
                    },
                    {
                        "frame": 15,
                        "enabled": False,
                        "x": 40,
                        "y": 49,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 15,
                    },
                ],
            },
        }
    ]
    key_frames = extract_key_frames(example)[0]['value']['sequence']
    assert len(key_frames) == 10
    assert key_frames[5]['x'] == 38
    assert key_frames[5]['y'] == 38
    assert key_frames[5]['width'] == 41
    assert key_frames[5]['height'] == 22
    assert key_frames[5]['rotation'] == 0
    assert key_frames[5]['time'] == 11
    assert key_frames[9]['x'] == 40
    assert key_frames[9]['y'] == 49
    assert key_frames[9]['width'] == 41
    assert key_frames[9]['height'] == 22
    assert key_frames[9]['rotation'] == 0
    assert key_frames[9]['time'] == 15
    assert key_frames[7]['x'] == 39
    assert key_frames[7]['y'] == 43.5
    assert key_frames[7]['width'] == 41
    assert key_frames[7]['height'] == 22
    assert key_frames[7]['rotation'] == 0
    assert key_frames[7]['auto']


def test_no_label_result():
    """
    Test frames extraction with no label and disabled in the end and frame count > disabled key frame
    """
    example = [
        {
            "id": "tJhYZLMC9G",
            "type": "videorectangle",
            "value": {
                "framesCount": 10000000,
                "sequence": [
                    {
                        "frame": 1,
                        "enabled": True,
                        "x": 38,
                        "y": 38,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 1.01,
                    },
                    {
                        "frame": 5,
                        "enabled": False,
                        "x": 40,
                        "y": 49,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 1.55,
                    },
                    {
                        "frame": 11,
                        "enabled": True,
                        "x": 38,
                        "y": 38,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 2.02,
                    },
                    {
                        "frame": 15,
                        "enabled": False,
                        "x": 40,
                        "y": 49,
                        "width": 41,
                        "height": 22,
                        "rotation": 0,
                        "time": 3.10,
                    },
                ],
            },
        }
    ]
    key_frames = extract_key_frames(example)[0]['value']['sequence']
    assert len(key_frames) == 10
    assert key_frames[5]['x'] == 38
    assert key_frames[5]['y'] == 38
    assert key_frames[5]['width'] == 41
    assert key_frames[5]['height'] == 22
    assert key_frames[5]['rotation'] == 0
    assert key_frames[9]['x'] == 40
    assert key_frames[9]['y'] == 49
    assert key_frames[9]['width'] == 41
    assert key_frames[9]['height'] == 22
    assert key_frames[9]['rotation'] == 0
    assert key_frames[7]['x'] == 39
    assert key_frames[7]['y'] == 43.5
    assert key_frames[7]['width'] == 41
    assert key_frames[7]['height'] == 22
    assert key_frames[7]['rotation'] == 0


def test_case_with_1_frame_inside_2_span():
    example = [
        {
            "id": "XgRSxLA2GG",
            "type": "videorectangle",
            "value": {
                "labels": ["Woman"],
                "sequence": [
                    {
                        "x": -0.818330605564648,
                        "y": -0.3364248045099079,
                        "time": 0.08,
                        "frame": 2,
                        "width": 18.494271685761046,
                        "height": 50.3364248045099,
                        "enabled": True,
                        "rotation": 0,
                    },
                    {
                        "x": 81.66939443535188,
                        "y": 49.70903800691037,
                        "time": 0.4,
                        "frame": 10,
                        "width": 18.494271685761046,
                        "height": 50.3364248045099,
                        "enabled": False,
                        "rotation": 0,
                    },
                    {
                        "x": 43.53518821603928,
                        "y": 31.378432442262238,
                        "time": 0.52,
                        "frame": 13,
                        "width": 18.494271685761046,
                        "height": 50.3364248045099,
                        "enabled": False,
                        "rotation": 0,
                    },
                    {
                        "x": -1.4729950900163666,
                        "y": 50,
                        "time": 0.64,
                        "frame": 16,
                        "width": 18.494271685761046,
                        "height": 50.3364248045099,
                        "enabled": True,
                        "rotation": 0,
                    },
                ],
                "framesCount": 299,
            },
            "origin": "manual",
            "to_name": "video",
            "from_name": "box",
        }
    ]
    key_frames = extract_key_frames(example)[0]['value']['sequence']
    assert len(key_frames) == 294
