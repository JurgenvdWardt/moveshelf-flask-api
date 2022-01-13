import os

from flask import Blueprint, request, jsonify
from api.core.jurgen_api import JurgenApi

api = Blueprint('api', __name__)
jurgen_api = JurgenApi()


@api.route('/upload', methods=['POST'])
def upload_gait():
    dataType = request.form.get('datatype')
    file = request.files.get('file')

    if file.filename == '':
        return 'File not found', 404

    clip_id = configure_standards_and_get_clipId(jurgen_api)
    existingAdditionalData = jurgen_api.getAdditionalData(clip_id)
    if file.filename in [data['originalFileName'] for data in existingAdditionalData]:
        return 'File already found in clip', 400

    filepath = os.getcwd() + '/temp/{}'.format(file.filename)
    file.save(filepath)

    result = jurgen_api.uploadAdditionalData(filepath, clip_id, dataType, file.filename)

    os.remove(filepath)

    return result


@api.route('/upload', methods=['GET'])
def get_uploads():
    clips = jurgen_api.getProjectClips(jurgen_api.setProject(), -1)
    filename = request.args.get('filename')

    result = []

    for clip in clips:
        # Check for existing data
        existingAdditionalData = jurgen_api.getAdditionalData(clip['id'])
        existingFileNames = [data['originalFileName'] for data in existingAdditionalData if
                             len(existingAdditionalData) > 0]
        for existingFileName in existingFileNames:
            if filename == existingFileName:
                result.append({
                    'clip': clip,
                    'file': filename
                })

    return jsonify(result), 200


def configure_standards_and_get_clipId(jurgen_api):
    projectId = jurgen_api.setProject()
    subjectDetails = jurgen_api.setSubject(projectId)
    session = jurgen_api.setSession(subjectDetails, projectId)
    condition = jurgen_api.setConditions(session)
    return jurgen_api.setTrial(session, condition)
