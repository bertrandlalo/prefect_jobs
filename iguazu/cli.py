import click

import iguazu


@click.command()
@click.option('-p', '--prefix',  default='iguazu', show_default=True,
              help='Docker prefix name.')
@click.option('-r', '--registry',
              help='Docker registry where the resulting images will be uploaded.')
def create_images(prefix, registry):
    # Fail early when docker is not present
    try:
        import docker
        client = docker.from_env()
    except ImportError:
        print('Building images requires the "docker" as dependency')
        raise

    app_version = iguazu.__version__
    # todo: semver match like quetzal

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
            l = line['stream'].strip()
            if l:
                click.secho(l)

    click.secho('Uploading images...', fg='blue')
    image.tag(full_tag)
    for line in client.images.push(full_tag, stream=True, decode=True):
        if 'error' in line:
            raise click.ClickException(line['error'].strip())
        if 'stream' in line:
            l = line['stream'].strip()
            if l:
                click.echo(l)


if __name__ == '__main__':
    create_images()
