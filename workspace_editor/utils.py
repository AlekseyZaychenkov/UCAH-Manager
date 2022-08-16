import logging
import os

from loader.models import Post, Compilation
from UCA_Manager.settings import PATH_TO_STORE
from loader.utils import generate_storage_patch, save_files
import shutil

from workspace_editor.models import CompilationHolder

log = logging.getLogger(__name__)

def copy_post_to(post_id, recipient_compilation_id, copy_files=False):
    compilation = Compilation.objects.get(id=recipient_compilation_id)

    old_post = Post.objects.get(id=post_id)

    # TODO: create storage path  user/workspace/schedule
    # savedFileAddresses = save_files(storagePath, file_urls) if storagePath is not None else None
    path = generate_storage_patch(PATH_TO_STORE, comp_id=recipient_compilation_id, others="createdForSchedule")
    saved_file_addresses = save_files(path, old_post.file_urls)
    print(f"copy_post_to() - old_post.text: {old_post.text}")

    new_post = Post.create(
        # information about original post
        blog_name             = old_post.blog_name,
        blog_url              = old_post.blog_url,
        id_in_social_network  = old_post.id_in_social_network,
        original_post_url     = old_post.original_post_url,
        posted_date           = old_post.posted_date,
        posted_timestamp      = old_post.posted_timestamp,
        tags                  = old_post.tags,
        text                  = old_post.text,
        file_urls             = old_post.file_urls,

        # information about search query parameters
        compilation_id        = recipient_compilation_id,

        # information for posting
        stored_file_urls      = saved_file_addresses,
        external_link_urls    = old_post.external_link_urls,

        # information after posted
        url                   = old_post.url,
        # # TODO: implement special map-like structure for storing published posts with statistic about them (postUrl1, likes, comments, likes under comments)
        # where_posted        = columns.Map(key_type=columns.Text, value_type=columns.Text, required=False)  # list of dicts "blogName: {'dateTime1 - postUrl1', 'dateTime2 - postUrl2', ...}"

        # information for administration notes and file storing
        description           = old_post.description
    )
    new_post.update()

    # TODO: redouble this fragment of code
    if compilation.post_ids is None:
        compilation.post_ids = [new_post.id]
    else:
        compilation.post_ids.append(new_post.id)

    compilation.update()

    return new_post.id


def delete_compilation_holder(holder_id):
    holder = CompilationHolder.objects.get(compilation_holder_id=holder_id)

    delete_compilation(holder.compilation_id)

    other_holders = CompilationHolder.objects.filter(workspace=holder.workspace_id)
    for oh in other_holders:
        oh.number_on_list -= 1
        oh.save()

    holder.delete()


def delete_compilation(compilation_id):
    compilation = Compilation.objects.get(id=compilation_id)

    post_ids = compilation.post_ids
    for post_id in post_ids:
        delete_post(post_id)

    compilation.delete()


def delete_post(post_id):
    post = Post.objects.get(id=post_id)

    if post:
        compilation_id = post.compilation_id
        compilation = Compilation.objects.get(id=compilation_id)

        if compilation:
            compilation.post_ids.remove(post.id)
            compilation.update()
        else:
            log.error(f"No compilation with id='{compilation_id}' for post id='{post.id}' ")

        if len(post.stored_file_urls) > 0:
            folder = post.stored_file_urls[0].parent
            for file in post.stored_file_urls:
                os.remove(file)
            if len(os.listdir(folder)) == 0:
                shutil.rmtree(folder)

        post.delete()

    else:
        log.error(f"No post with id='{post.id}' ")