import click

from bibliothek.bibliothek import Bibliothek


@click.help_option()
@click.group()
def main() -> None:
    pass


@main.command()
def get_projects() -> None:
    bibliothek = Bibliothek()
    projects_list = ', '.join(bibliothek.get_projects())
    print(f"Available projects: {projects_list}")


@main.command()
@click.argument("project-id")
def get_project(project_id: str) -> None:
    bibliothek = Bibliothek()
    project = bibliothek.get_project(project_id)
    print(
        f"Project ID: {project.project_id}\n"
        f"Project Name: {project.project_name}\n"
        f"Version Groups: {', '.join(project.version_groups)}\n"
        f"Versions: {', '.join(project.versions)}"
    )


@main.command()
@click.argument("project-id")
@click.argument("version-group")
def get_version_group(project_id: str, version_group: str) -> None:
    bibliothek = Bibliothek()
    bibliothek_version_group = bibliothek.get_version_group(project_id, version_group)
    print(
        f"Project ID: {bibliothek_version_group.project_id}\n"
        f"Project Name: {bibliothek_version_group.project_name}\n"
        f"Version Group: {bibliothek_version_group.version_group}\n"
        f"Versions: {', '.join(bibliothek_version_group.versions)}"
    )


@main.command()
@click.argument("project-id")
@click.argument("version-group")
def get_version_group_builds(project_id: str, version_group: str) -> None:
    bibliothek = Bibliothek()
    version_group_builds = bibliothek.get_version_group_builds(project_id, version_group)
    print(
        f"Project ID: {version_group_builds.project_id}\n"
        f"Project Name: {version_group_builds.project_name}\n"
        f"Version Group: {version_group_builds.version_group}\n"
        f"Versions: {', '.join(version_group_builds.versions)}\n"
        f"Builds: {', '.join([str(i.build) for i in version_group_builds.builds])}"
    )


@main.command()
@click.argument("project-id")
@click.argument("version")
def get_version(project_id: str, version: str) -> None:
    bibliothek = Bibliothek()
    bibliothek_version = bibliothek.get_version(project_id, version)
    print(
        f"Project ID: {bibliothek_version.project_id}\n"
        f"Project Name: {bibliothek_version.project_name}\n"
        f"Version: {bibliothek_version.version}\n"
        f"Builds: {','.join([str(i) for i in bibliothek_version.builds])}"
    )


@main.command()
@click.argument("project-id")
@click.argument("version")
@click.argument("build", type=click.INT)
def get_build(project_id: str, version: str, build: int) -> None:
    bibliothek = Bibliothek()
    bibliothek_build = bibliothek.get_build(project_id, version, build)

    changes = []
    for change in bibliothek_build.changes:
        changes.append(f" - [{change.commit[:7]}] {change.summary}")

    print(
        f"Project ID: {bibliothek_build.project_id}\n"
        f"Project Name: {bibliothek_build.project_name}\n"
        f"Version: {bibliothek_build.version}\n"
        f"Build: {bibliothek_build.build}\n"
        f"Promoted: {bibliothek_build.promoted}\n"
        f"Time: {bibliothek_build.time.strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"Channel: {bibliothek_build.channel}\n"
        f"Changes:\n" +
        '\n'.join(changes) +
        "\n\n"
        f"Downloads: {', '.join(bibliothek_build.downloads.keys())}"
    )


@main.command()
@click.argument("project-id")
@click.argument("version")
@click.argument("build", type=click.INT)
@click.argument("filename")
def download_build(project_id: str, version: str, build: int, filename: str) -> None:
    bibliothek = Bibliothek()

    bibliothek_build = bibliothek.get_build(project_id, version, build)

    print(
        f"Project ID: {bibliothek_build.project_id}\n"
        f"Project Name: {bibliothek_build.project_name}\n"
        f"Build: {bibliothek_build.build}\n"
        f"Promoted: {bibliothek_build.promoted}"
    )

    with click.progressbar(length=2, label=f"Downloading {project_id}/{version}@{build}") as bar:
        bar.update(1)
        downloaded_build = bibliothek.download_build(project_id, version, build, filename)
        bar.update(2)
        bar.finish()

    hash_to_compare = None
    for download_key in bibliothek_build.downloads.keys():
        if bibliothek_build.downloads[download_key].name == filename:
            hash_to_compare = bibliothek_build.downloads[download_key].sha256

    if hash_to_compare is None:
        raise Exception("Download not found.")

    hashes = bibliothek.check_hash(downloaded_build.getvalue(), hash_to_compare)

    print(f"Matching Hashes: {hashes}")

    with open(filename, 'wb') as handle:
        handle.write(downloaded_build.getvalue())

    print(f"File saved as {filename}")
