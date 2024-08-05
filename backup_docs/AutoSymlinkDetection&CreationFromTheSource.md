# auto symlink detection & creation from the source
## what is an auto symbolic link (symlink) creation?
this feature is about the streamlined auto symlink creation process with spaship. enable this feature through the spaship manager, allowing automatic extraction and deployment of symlinks. ensure validity, track status, and enjoy seamless integration within the file system, all with the transparency and accountability provided by the spaship manager.
## key points about auto symlink creation :
1. **enablement through spaship manager:** to leverage auto symlink creation, users must first enable this feature in the spaship manager. this setting is specific to each application and environment.
1. **automatic extraction and deployment:** spaship simplifies the process by automatically extracting all symlinks from the application's source during deployment. once deployed, the tool proceeds to create the symlinks based on the provided specifications.
1. **providing valid symlinks:** users are required to provide valid symlinks, ensuring correctness and reliability. these symlinks should be specified with respect to the relative path, facilitating seamless integration within the file system.
1. **scheduled creation process:** auto symlink creation involves a three-step process. initially, spaship extracts the symlinks, followed by scheduling the symlink creation. after a successful deployment, the creation of symlinks is automatically initiated within two minutes, streamlining the entire process.
1. **track symlink status:** throughout the auto symlink creation process, users can conveniently monitor the status of symlinks, whether they are scheduled, completed, or encountered any issues. this visibility is facilitated through the spaship manager, ensuring transparency and accountability.
### process to use the auto-symlink creation :
1. **use relative paths:** when specifying symlinks, always opt for relative paths from the current directory. this ensures the creation of valid symlinks, facilitating smooth navigation within the file system.
   ![use relative paths](./images/auto_symlink_1.png)
1. **symlinks in nested directory:** spaship extends its functionality to extract symlinks from any nested directories uploaded with the archive. however, users must ensure to the same creation process,
   ![symlinks in nested directory](./images/auto_symlink_2.png)
1. **avoid absolute paths:** refrain from providing absolute paths, as they may lead to incorrect symlink creation. instead, focus on relative paths to ensure accuracy. additionally, minimize the use of "../" to mitigate potential issues arising from missing directories in the uploaded archive. if erroneous symlinks are created, they can easily be deleted via the spaship manager.
   ![avoid absolute paths](./images/auto_symlink_3.png)
1. **enable auto symlink creation** : to enable automatic symlink creation for a specific application, navigate to the spaship manager. select the desired application and locate the settings menu. from there, enable the automatic symlink creation feature to streamline symlink management and enhance deployment efficiency and the perform the normal deployment.
![enable auto symlink creation a](./images/auto_symlink_4a.png) 
![enable auto symlink creation b](./images/auto_symlink_4b.png) 
1. **monitor symlink creation:** navigate to the spaship manager to track the status of symlink creation. here, you can observe when the creation process has been scheduled, providing transparency and oversight.
![monitor symlink creation a](./images/auto_symlink_5a.png)  
![monitor symlink creation b](./images/auto_symlink_5a.png)  
1. **automatic creation confirmation:** approximately two minutes after deployment, check the spaship manager for confirmation that symlinks have been automatically created. this automated process streamlines symlink management, allowing you to proceed with confidence.
![automatic creation confirmation a](./images/auto_symlink_5a.png)
![automatic creation confirmation b](./images/auto_symlink_5a.png)
in this way, automated symlinks can be created from the source, ensuring efficient deployment and reliable auto-symlink integration with spaship's streamlined features.