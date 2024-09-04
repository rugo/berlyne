import os
from time import sleep

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from vmmanage.deploy_controller import install_available_problems, run_on_existing
from vmmanage.models import Problem


class Command(BaseCommand):
    help = "Updates the database with changes from the challenge repo."

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--install",
            action="store_true",
            help="Automatically install new problems from the repo.",
        )

        parser.add_argument(
            "--delete",
            action="store_true",
            help="Automatically delete problems that don't exist in the fs anymore.",
        )

    def handle(self, *args, **options):
        for problem in Problem.objects.all():

            if not os.path.isdir(problem.relative_path):
                print(
                    f"Problem path {problem.path} (Problem {problem.name}) doesn't exist. Skipping."
                )
                if options["delete"]:
                    print(f"Deleting problem {problem.name}/{problem.slug}, as it is not in the fs anymore.")
                    problem.delete()
                continue

            if problem.version_hash == problem.calc_version_hash():
                continue

            print(f"Processing {problem.name}/{problem.slug} from {problem.path} has changed! Updating...")
            problem.update_meta()
            # The actual rebuild is launched asynchronously.
            # However, asynchronous jobs with autotask only work on
            # the production DB. So for the local test setup we work synchronously
            if settings.DEBUG:
                problem.get_vagrant().rebuild()
            else:
                run_on_existing("rebuild", problem.vm)

        if options["install"]:
            for success, path, error in install_available_problems():
                if success:
                    print(f"Launched install job for {path}.")
                else:
                    error_type = type(error).__name__
                    print(
                        self.style.ERROR(
                            f"Could not launch job for {path}: {error_type} - {error}"
                        )
                    )
