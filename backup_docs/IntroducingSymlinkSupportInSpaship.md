# introducing symlink support in spaship
## what is a symbolic link (symlink)?
symbolic links, often referred to as symlinks, are a crucial aspect of file systems in many unix-like operating systems, including linux, rhel, fedora, and others. they are files that serve as pointers to other files or directories, enabling users to access them easily through a specified path. this article delves into what symbolic links are and how they can be used, particularly in the context of spaship to establish connections between multiple applications.
## key points about symlink:
here are some key points to keep in mind when working with symbolic links:
1. **application deployment and environment:** to create symbolic links between applications using spaship, you need to have the respective applications deployed in a specific environment.
2. **using path names as prefixes:** when defining the path for a symlink, you use the path name as the prefix of the directory name. for instance, if your application is hosted at a "dx-source" path and you want to link to "index.html" within it, the input would be "dx-source/index.html".
3. **using rootspa for base path:** to create a symlink from or to the base path (/), use "rootspa" as the prefix of the directory.
4. **handling nested paths:** if dealing with nested paths, substitute slashes with underscores. for example, if the path is "nested/path" and the file is index.html, the input for the symlink would be "nested_path/index.html".
5. **permission needed to use symlink:** as of now, you must have "application creation" permission to create the symlink. to know more about rbac in spaship you can read [this source blog](https://source.redhat.com/groups/public/spaship/blog_article/introduction_to_rbac_feature_in_spaship).
## process for using symlink from the spaship manager:
let's walk through the process of utilizing symbolic links in spaship manager to establish connections between single page applications (spas).
### step 1.0: deploy applications in the specific property
ensure that the applications you intend to establish a symlink between are deployed within the specific property. for a demonstration, let's consider two applications deployed on a property.
![step 1.0](./images/symlink_support_step1.png)
### step 1.1: directory structure
here is the directory structure of the property. we'll create a symlink in the "dx-target", as you can see currently it only contains "index.html".
![step 1.1](./images/symlink_support_step1_1.png)
### step 2.0: configure symlink in property settings
navigate to the settings section of the property within spaship manager. look for the symlink option and provide the symlink source directory, such as "dx-source/index.html", and the target directory, such as "dx-target/symlink.html". this configuration establishes a symlink between the specified paths for the spas. you'll also find the list of symlinks in the list section.
![step 2.0](./images/symlink_support_step2.png)
### step 2.1: check the symlink creation
now here you can see that symlink has been created in the "dx-target".
![step 2.1](./images/symlink_support_step2_1.png)
### step 2.2: add multiple symlink
you can also add multiple symlinks; it will be created and you can see it from the symlink list section.
![step 2.2](./images/symlink_support_step2_2.png)
![step 2.2](./images/symlink_support_step2_3.png)
## restrictions & scope of enhancements:
1. **deletion and updation feature:** currently, once a symlink is created, it cannot be deleted. future releases of spaship will introduce features for symlink deletion and updating to enhance symlink management.
2. **auto population of spa names:** future updates of spaship will incorporate an auto-population feature for spa names in the source and target directories, streamlining the symlink creation process.
by following these steps and understanding the principles of symbolic links, you can effectively manage connections between applications using symbolic links within spaship. symbolic links offer a flexible and powerful way to organize and navigate files and directories in a file system.