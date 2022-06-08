import os
import traceback

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def process_generic_document(request, instance, document_type=None, *args, **kwargs):
    print("process_generic_document")
    print(request.data)
    try:
        action = request.data.get("action")
        input_name = request.data.get("input_name")
        comms_log_id = request.data.get("comms_log_id")
        comms_instance = None

        if document_type == "comms_log" and comms_log_id and comms_log_id != "null":
            comms_instance = instance.comms_logs.get(id=comms_log_id)
        elif document_type == "comms_log":
            comms_instance = instance.comms_logs.create()

        if action == "list":
            pass
        elif action == "delete":
            delete_document(
                request, instance, comms_instance, document_type, input_name
            )
        elif action == "cancel":
            deleted = cancel_document(
                request, instance, comms_instance, document_type, input_name
            )
        elif action == "save":
            save_document(request, instance, comms_instance, document_type, input_name)

        # HTTP Response varies by action and instance type
        if comms_instance and action == "cancel" and deleted:
            return deleted
        elif comms_instance:
            returned_file_data = [
                dict(
                    file=d._file.url,
                    id=d.id,
                    name=d.name,
                )
                for d in comms_instance.documents.all()
                if d._file
            ]
            return {
                "filedata": returned_file_data,
                "comms_instance_id": comms_instance.id,
            }
        # example document_type
        elif input_name:
            if document_type == "deed_poll_document":
                documents_qs = instance.deed_poll_documents
            elif document_type == "supporting_document":
                documents_qs = instance.supporting_documents
            elif document_type == "exclusive_use_document":
                documents_qs = instance.exclusive_use_documents
            elif document_type == "long_term_use_document":
                documents_qs = instance.long_term_use_documents
            elif document_type == "consistent_purpose_document":
                documents_qs = instance.consistent_purpose_documents
            elif document_type == "consistent_plan_document":
                documents_qs = instance.consistent_plan_documents
            elif document_type == "clearing_vegetation_document":
                documents_qs = instance.clearing_vegetation_documents
            elif document_type == "ground_disturbing_works_document":
                documents_qs = instance.ground_disturbing_works_documents
            elif document_type == "heritage_site_document":
                documents_qs = instance.heritage_site_documents
            elif document_type == "environmentally_sensitive_document":
                documents_qs = instance.environmentally_sensitive_documents
            elif document_type == "wetlands_impact_document":
                documents_qs = instance.wetlands_impact_documents
            elif document_type == "building_required_document":
                documents_qs = instance.building_required_documents
            elif document_type == "significant_change_document":
                documents_qs = instance.significant_change_documents
            elif document_type == "aboriginal_site_document":
                documents_qs = instance.aboriginal_site_documents
            elif document_type == "native_title_consultation_document":
                documents_qs = instance.native_title_consultation_documents
            elif document_type == "mining_tenement_document":
                documents_qs = instance.mining_tenement_documents
            elif document_type == "profit_and_loss_document":
                documents_qs = instance.profit_and_loss_documents
            elif document_type == "cash_flow_document":
                documents_qs = instance.cash_flow_documents
            elif document_type == "capital_investment_document":
                documents_qs = instance.capital_investment_documents
            elif document_type == "financial_capacity_document":
                documents_qs = instance.financial_capacity_documents
            elif document_type == "mining_tenement_document":
                documents_qs = instance.mining_tenement_documents
            elif document_type == "available_activities_document":
                documents_qs = instance.available_activities_documents
            elif document_type == "market_analysis_document":
                documents_qs = instance.market_analysis_documents
            elif document_type == "staffing_document":
                documents_qs = instance.staffing_documents
            elif document_type == "key_personnel_document":
                documents_qs = instance.key_personnel_documents
            elif document_type == "key_milestones_document":
                documents_qs = instance.key_milestones_documents
            elif document_type == "risk_factors_document":
                documents_qs = instance.risk_factors_documents
            elif document_type == "legislative_requirements_document":
                documents_qs = instance.legislative_requirements_documents
            elif document_type == "shapefile_document":
                documents_qs = instance.shapefile_documents

            returned_file_data = [
                dict(
                    file=d._file.url,
                    id=d.id,
                    name=d.name,
                )
                for d in documents_qs.filter(input_name=input_name)
                if d._file
            ]
            return {"filedata": returned_file_data}
        else:
            # not used
            returned_file_data = [
                dict(
                    file=d._file.url,
                    id=d.id,
                    name=d.name,
                )
                for d in instance.documents.all()
                if d._file
            ]
            return {"filedata": returned_file_data}

    except Exception as e:
        print(traceback.print_exc())
        raise e


def delete_document(request, instance, comms_instance, document_type, input_name=None):
    document_id = request.data.get("document_id")
    if "document_id" in request.data:
        if document_type == "deed_poll_document":
            document = instance.deed_poll_documents.get(id=document_id)
        elif document_type == "temp_document":
            document = instance.documents.get(id=document_id)
        elif document_type == "supporting_document":
            document = instance.supporting_documents.get(id=document_id)
        elif document_type == "exclusive_use_document":
            document = instance.exclusive_use_documents.get(id=document_id)
        elif document_type == "long_term_use_document":
            document = instance.long_term_use_documents.get(id=document_id)
        elif document_type == "consistent_purpose_document":
            document = instance.consistent_purpose_documents.get(id=document_id)
        elif document_type == "consistent_plan_document":
            document = instance.consistent_plan_documents.get(id=document_id)
        elif document_type == "clearing_vegetation_document":
            document = instance.clearing_vegetation_documents.get(id=document_id)
        elif document_type == "ground_disturbing_works_document":
            document = instance.ground_disturbing_works_documents.get(id=document_id)
        elif document_type == "heritage_site_document":
            document = instance.heritage_site_documents.get(id=document_id)
        elif document_type == "environmentally_sensitive_document":
            document = instance.environmentally_sensitive_documents.get(id=document_id)
        elif document_type == "wetlands_impact_document":
            document = instance.wetlands_impact_documents.get(id=document_id)
        elif document_type == "building_required_document":
            document = instance.building_required_documents.get(id=document_id)
        elif document_type == "significant_change_document":
            document = instance.significant_change_documents.get(id=document_id)
        elif document_type == "aboriginal_site_document":
            document = instance.aboriginal_site_documents.get(id=document_id)
        elif document_type == "native_title_consultation_document":
            document = instance.native_title_consultation_documents.get(id=document_id)
        elif document_type == "mining_tenement_document":
            document = instance.mining_tenement_documents.get(id=document_id)
        elif document_type == "profit_and_loss_document":
            document = instance.profit_and_loss_documents.get(id=document_id)
        elif document_type == "cash_flow_document":
            document = instance.cash_flow_documents.get(id=document_id)
        elif document_type == "capital_investment_document":
            document = instance.capital_investment_documents.get(id=document_id)
        elif document_type == "financial_capacity_document":
            document = instance.financial_capacity_documents.get(id=document_id)
        elif document_type == "available_activities_document":
            document = instance.available_activities_documents.get(id=document_id)
        elif document_type == "market_analysis_document":
            document = instance.market_analysis_documents.get(id=document_id)
        elif document_type == "staffing_document":
            document = instance.staffing_documents.get(id=document_id)
        elif document_type == "key_personnel_document":
            document = instance.key_personnel_documents.get(id=document_id)
        elif document_type == "key_milestones_document":
            document = instance.key_milestones_documents.get(id=document_id)
        elif document_type == "risk_factors_document":
            document = instance.risk_factors_documents.get(id=document_id)
        elif document_type == "legislative_requirements_document":
            document = instance.legislative_requirements_documents.get(id=document_id)
        elif document_type == "shapefile_document":
            document = instance.shapefile_documents.get(id=document_id)

    # comms_log doc store delete
    elif comms_instance and "document_id" in request.data:
        document = comms_instance.documents.get(id=document_id)

    # default doc store delete
    elif "document_id" in request.data:
        document = instance.documents.get(id=document_id)

    if document._file and os.path.isfile(document._file.path):
        os.remove(document._file.path)

    if document:
        document.delete()


def cancel_document(request, instance, comms_instance, document_type, input_name=None):
    if document_type in [
        "deed_poll_document",
        "supporting_document",
        "exclusive_use_document",
        "long_term_use_document",
        "consistent_purpose_document",
        "consistent_plan_document",
        "clearing_vegetation_document",
        "ground_disturbing_works_document",
        "heritage_site_document",
        "environmentally_sensitive_document",
        "wetlands_impact_document",
        "building_required_document",
        "significant_change_document",
        "aboriginal_site_document",
        "native_title_consultation_document",
        "mining_tenement_document",
        "profit_and_loss_document",
        "cash_flow_document",
        "capital_investment_document",
        "financial_capacity_document",
        "available_activities_document",
        "market_analysis_document",
        "staffing_document",
        "key_personnel_document",
        "key_milestones_document",
        "risk_factors_document",
        "legislative_requirements_document",
    ]:

        if comms_instance:
            document_list = comms_instance.documents.all()
        else:
            document_list = instance.documents.all()

    for document in document_list:
        if document._file and os.path.isfile(document._file.path):
            os.remove(document._file.path)
        document.delete()

    if comms_instance:
        return comms_instance.delete()


def save_document(request, instance, comms_instance, document_type, input_name=None):
    # example document_type
    if "filename" in request.data and input_name:
        filename = request.data.get("filename")
        _file = request.data.get("_file")

        if document_type == "deed_poll_document":
            document = instance.deed_poll_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/deed_poll_documents/{}"
        elif document_type == "supporting_document":
            document = instance.supporting_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/supporting_documents/{}"
        elif document_type == "exclusive_use_document":
            document = instance.exclusive_use_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/exclusive_use_documents/{}"
        elif document_type == "long_term_use_document":
            document = instance.long_term_use_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/long_term_use_documents/{}"
        elif document_type == "consistent_purpose_document":
            document = instance.consistent_purpose_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/consistent_purpose_documents/{}"
        elif document_type == "consistent_plan_document":
            document = instance.consistent_plan_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/consistent_plan_documents/{}"
        elif document_type == "clearing_vegetation_document":
            document = instance.clearing_vegetation_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/clearing_vegetation_documents/{}"
        elif document_type == "ground_disturbing_works_document":
            document = instance.ground_disturbing_works_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/ground_disturbing_works_documents/{}"
        elif document_type == "heritage_site_document":
            document = instance.heritage_site_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/heritage_site_documents/{}"
        elif document_type == "environmentally_sensitive_document":
            document = instance.environmentally_sensitive_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = (
                "{}/proposals/{}/environmentally_sensitive_documents/{}"
            )
        elif document_type == "wetlands_impact_document":
            document = instance.wetlands_impact_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/wetlands_impact_documents/{}"
        elif document_type == "building_required_document":
            document = instance.building_required_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/building_required_documents/{}"
        elif document_type == "significant_change_document":
            document = instance.significant_change_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/significant_change_documents/{}"
        elif document_type == "aboriginal_site_document":
            document = instance.aboriginal_site_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/aboriginal_site_documents/{}"
        elif document_type == "native_title_consultation_document":
            document = instance.native_title_consultation_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = (
                "{}/proposals/{}/native_title_consultation_documents/{}"
            )
        elif document_type == "mining_tenement_document":
            document = instance.mining_tenement_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/mining_tenement_documents/{}"
        elif document_type == "profit_and_loss_document":
            document = instance.profit_and_loss_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/profit_and_loss_documents/{}"
        elif document_type == "cash_flow_document":
            document = instance.cash_flow_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/cash_flow_documents/{}"
        elif document_type == "capital_investment_document":
            document = instance.capital_investment_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/capital_investment_documents/{}"
        elif document_type == "financial_capacity_document":
            document = instance.financial_capacity_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/financial_capacity_documents/{}"
        elif document_type == "available_activities_document":
            document = instance.available_activities_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/available_activities_documents/{}"
        elif document_type == "market_analysis_document":
            document = instance.market_analysis_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/market_analysis_documents/{}"
        elif document_type == "staffing_document":
            document = instance.staffing_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/staffing_documents/{}"
        elif document_type == "key_personnel_document":
            document = instance.key_personnel_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/key_personnel_documents/{}"
        elif document_type == "key_milestones_document":
            document = instance.key_milestones_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/key_milestones_documents/{}"
        elif document_type == "risk_factors_document":
            document = instance.risk_factors_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/risk_factors_documents/{}"
        elif document_type == "legislative_requirements_document":
            document = instance.legislative_requirements_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/legislative_requirements_documents/{}"
        elif document_type == "shapefile_document":
            document = instance.shapefile_documents.get_or_create(
                input_name=input_name, name=filename
            )[0]
            path_format_string = "{}/proposals/{}/shapefile_documents/{}"

        path = default_storage.save(
            path_format_string.format(settings.MEDIA_APP_DIR, instance.id, filename),
            ContentFile(_file.read()),
        )
        document._file = path
        document.save()

    # comms_log doc store save
    elif comms_instance and "filename" in request.data:
        filename = request.data.get("filename")
        _file = request.data.get("_file")

        document = comms_instance.documents.get_or_create(name=filename)[0]
        path = default_storage.save(
            "{}/{}/communications/{}/documents/{}".format(
                instance._meta.model_name, instance.id, comms_instance.id, filename
            ),
            ContentFile(_file.read()),
        )

        document._file = path
        document.save()

    # default doc store save
    elif "filename" in request.data:
        filename = request.data.get("filename")
        _file = request.data.get("_file")

        document = instance.documents.get_or_create(name=filename)[0]
        path = default_storage.save(
            "{}/{}/documents/{}".format(
                instance._meta.model_name, instance.id, filename
            ),
            ContentFile(_file.read()),
        )

        document._file = path
        document.save()


# For transferring files from temp doc objs to default doc objs
def save_default_document_obj(instance, temp_document):
    document = instance.documents.get_or_create(name=temp_document.name)[0]
    path = default_storage.save(
        "{}/{}/documents/{}".format(
            instance._meta.model_name, instance.id, temp_document.name
        ),
        temp_document._file,
    )

    document._file = path
    document.save()


def save_vessel_registration_document_obj(instance, temp_document):
    document = instance.vessel_registration_documents.get_or_create(
        input_name="vessel_registration_document", name=temp_document.name
    )[0]
    path = default_storage.save(
        "{}/{}/documents/{}".format(
            instance._meta.model_name,
            instance.id,
            temp_document.name,
        ),
        temp_document._file,
    )

    document._file = path
    document.save()
