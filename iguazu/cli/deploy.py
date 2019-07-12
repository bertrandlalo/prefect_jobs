import click
import docker

import iguazu


@click.group('deploy')
def deploy_group():
    """Deployment commands and helpers"""
    pass


@deploy_group.command()
@click.option('-p', '--prefix',  default='iguazu', show_default=True,
              help='Docker image prefix name. Images will be tagged '
                   'PREFIX/iguazu:VERSION',
              metavar='PREFIX')
@click.option('-r', '--registry',
              help='Docker registry where the resulting images will be uploaded. '
                   'For example, for Google Cloud Registry, use gcr.io/your_project_id')
def images(prefix, registry):
    """ Deploy iguazu Docker images to a Docker registry"""
    client = docker.from_env()

    app_version = iguazu.__version__
    # TODO: semver match like quetzal

    click.secho('Building images...', fg='blue')
    tag = f'{prefix}/iguazu:{app_version}'
    full_tag = f'{registry}/{tag}'
    image, logs = client.images.build(
        path='.',
        buildargs=None,
        tag=tag,
    )
    for line in logs:
        if 'stream' in line:
            ls = line['stream'].strip()
            if ls:
                click.secho(ls)

    click.secho('Uploading images...', fg='blue')
    image.tag(full_tag)
    for line in client.images.push(full_tag, stream=True, decode=True):
        if 'error' in line:
            raise click.ClickException(line['error'].strip())
        if 'stream' in line:
            ls = line['stream'].strip()
            if ls:
                click.echo(ls)
