---
title: Arcamens Docs
---

### Intro

Arcamens was designed to allow a high level of communication and collaboration by teams.
It implements so called Kanban Boards and Timelines.
Timelines can be used to delegate isolated tasks, share information, events, questions and even store information that is
pertinent to a project.

The aim of arcamens is being as flexible as possible. It allows better dealing with high payloads of information and facilitates
better organization of information. Arcamens is ideal for all kind of teams whose motto is simplicity and flexibility.

The boards, lists and cards are structured in a tree-like manner what allows a succinct perspective
of the information that is relevant to the board team.

The following image displays an example set of boards:

![arcamens-boards-0](/static/site_app/help/arcamens-boards-0.png)

After accessing the board, its lists are shown.

![arcamens-boards-1](/static/site_app/help/arcamens-boards-1.png)

Once a list is accessed by clicking on its link name it displays all the cards
that it holds.

![arcamens-boards-2](/static/site_app/help/arcamens-boards-2.png)

Arcamens boards allow one to deal with a high amount of cards in a very advantageous manner
because information is more visible. It allows one to pin certain lists that are often used
thus allowing quick access of content.

Pinning an element is as easy as clicking on the clip icon as shown below:

![arcamens-boards-3](/static/site_app/help/arcamens-boards-3.png)

**Note:** You can pin boards, lists, cards or timelines.

Arcamens makes usage of cut/copy for moving cards around, it is much more efficient than
the usual drag&drop approach.  You can cut several cards, these will stay on the clipboard
when you're ready just paste them somewhere.

### Board Creation

You can create as many boards as you desire. For creating a new board just click on Home at the navbar
and then use the popup menu by clicking the wrench icon shown at this image:

![board-creation-0](/static/site_app/help/board-creation-0.png)

You would get:

![board-creation-1](/static/site_app/help/board-creation-1.png)

One may find it necessary to have boards that are related to the same project, in such situations
it is possible to set their descriptions with a slug to group them according to their project.

Imagine you have a project named arcamens that has many plugins, you have a team for each one of the plugins.
You could come up with boards description like:



    Arcamens/Github
    Arcamens/Bitbucket
    

Then you can use your board filter with a pattern like:


    Arcamens/
    

It would display just boards that meet that slug.

**See:** [Collection Filter](#collection-filter)

### List Creation

Lists are placed inside boards, After accessing the board link name you can
create new lists for the board.

For such click on +List link button.

![list-creation-0](/static/site_app/help/list-creation-0.png)

You would get:

![list-creation-1](/static/site_app/help/list-creation-1.png)

You can set slugs for lists as well, you could handle a project with many plugins
using the approach of setting slugs for each one of your project plugins as follows:


    Bitbucket/Todo
    Github/Todo
    Bitbucket/Doing
    Github/Doing
    
    ...
    

It allows designing your project workflow without creating multiple
boards for its plugins.

### Card Creation

Card are the entities which contain actual information pieces.

Cards are created inside lists, after accessing a list just click on +Card:

![card-creation-0](/static/site_app/help/card-creation-0.png)

You would get:

![card-creation-1](/static/site_app/help/card-creation-1.png)

The card label field is used to give a short description of the task, the data field
can contain markdown content and should be used when the content is too long.
After filling the fields and creating your task, you would get the view of the card:

![card-creation-2](/static/site_app/help/card-creation-2.png)

**Note:** Click on Up to get back to the card list.

You can change all attributes for the card there, whenever an attribute is changed
then an event is fired. All users who are related to the card will get notified.
These users are those who belong to the card board or are assigned to the card.

### Card Edition

### Events

Whenever an user creates or updates content then an event is fired. The events
are means of knowing what is going on with your teams.

![events-9](/static/site_app/help/events-0.png)

The action that was performed can be commented on thus giving constructive criticism about your peers
work.

Events will carry links to the objects that are related to the user action. You can left click on the links
and inspect the cards, lists, etc in the same browser tab or just middle click and open them in new browser
tabs.

When you finished checking an user action you can mark the event as seen then it will be no longer listed in the
Events dialog but you can still access it through your logs.

### Card Workers

After a card is created it can be assigned to someone for its execution by clicking on Workers:

![card-workers-0](/static/site_app/help/card-workers-0.png)

You would get:

![card-workers-1](/static/site_app/help/card-workers-1.png)

Type a string that matches either the user name or email then hit enter.
So you will be able to add users to the card task.

**See:** [Advanced User Search](#advanced-user-search)

### Board Permissions

A board will have a owner (the one who has created it), admins and members. The owner
is the only one who can make a member become an admin. Admins are allowed to add/remove members to the board
but members aren't allowed to remove peers.

For adding new members to the board (assuming you're the owner or an admin), just access the board 
then click on the wrench icon:

![board-permissions-0](/static/site_app/help/board-permissions-0.png)

Then click on Members, you would get:

![board-permissions-1](/static/site_app/help/board-permissions-1.png)

You can search users by using tag, email or name attributes, then add users.

**See:** [Advanced User Search](#advanced-user-search)

After binding/unbinding a given user to a board he/she will get notified of it.

### Tag Creation

You can tag all kind of content in arcamens, for such you need to create tags first. Everyone is allowed
to create new tags, when a tag is created an event is fired and everyone in the organization gets aware of it.

Click on the wrench icon on the organization menu:

![tag-creation-0](/static/site_app/help/tag-creation-0.png)

Then click on Tags:


![tag-creation-1](/static/site_app/help/tag-creation-1.png)

You would get:

![tag-creation-2](/static/site_app/help/tag-creation-2.png)

Notice that if your organization has many tags then you can look up a given tag by its name or description.
Just insert the pattern and hit enter then you'll get all tags that match the criterea.

Clicking on the plus sign it gives you:

![tag-creation-3](/static/site_app/help/tag-creation-3.png)

Fill the tag name and description and then click on Create.

![tag-creation-4](/static/site_app/help/tag-creation-4.png)

### Card Tags

Tags are a powerful mean of classifying content, arcamens allows you to tag cards, posts and users.
For tagging a given card just access the card by clicking on its label link.

![card-tags-0](/static/site_app/help/card-tags-0.png)

Then you'll view the card attributes.

![card-tags-1](/static/site_app/help/card-tags-1.png)

Click on Tags button at the card toolbar:

![card-tags-2](/static/site_app/help/card-tags-2.png)

Then you'll be able to manage the card tags:

![card-tags-3](/static/site_app/help/card-tags-3.png)

If you add/remove a tag to a card then everyone who is related to the card will get notified. 
You can look up the card tags by typing some pattern that shows on the tag name/description then hit enter.
It is useful when your organization has many tags.

### Card Search

In order to perform global card search just click on: Cards
at the navbar.

![card-search-0](/static/site_app/help/card-search-0.png)

You would get:

![card-search-1](/static/site_app/help/card-search-1.png)

with the above search/filter pattern it finds all cards
that contain the strings 'render' and 'template' either
in the label or data attribute. The data attribute of a card
it is the one that carries markdown.

If you defined as search pattern:

~~~
python django + render template + form
~~~

It would list all cards that contain the strings 'python django', 'render template'
ad 'form' either in the label or data attribute.

Notice that if you wanted the search pattern to be matched against archived cards instead,
then it would be necessary to mark the field Done as checked.


**See:** [Advanced Card Search](#advanced-card-search)

### Search for Card Tasks 

In arcamens there is a generic concept of task, a card becomes a task when it is
assigned to someone. When the task is accomplished then one can just archive it. 
The card will remain available for later inspection.

In order to search for active or archived cards that contain bound workers to, just click on the Tasks/Cards
at the navbar:

**Note:** The mechanism will match the search pattern against all cards that can be accessed by you.

![search-for-card-tasks-0](/static/site_app/help/search-for-card-tasks-0.png)

From the dialog window you can search through all cards that have at least one user
bound to. 

![search-for-card-tasks-1](/static/site_app/help/search-for-card-tasks-1.png)

**Assigned to me**

When this option is checked then the filter pattern will be matched
against all cards that were assigned to you.

**Created by Me**

When this option is checked then the filter pattern will match
all cards that were assigned to someone and the owner is you.

**Done**

This option allows to search for archived cards instead of active ones.

In the above example it finds all cards that are assigned to you
and contain the strings 'bug' and 'timezone' either in the label or data attributes.

You can get more than one match depending on the pattern and the existing cards.
Once you have filtered the cards then you can click on the card link and open it in the
actual browser tab or just right click and open in a new tab.

**See:** [Advanced Card Search](#advanced-card-search)

### Organization Creation

Organizations can serve on multiple purposes depending on the kind of business and size. 
You can map a team to an organization, a business branch to an organization or even handle all your
business team in a single organization. 

It all depends on how big your business is and on your necessities of designing your business workflow.

For creating an organization just click on your current organization icon at the navbar:

![organization-creation-0](/static/site_app/help/organization-creation-0.png)

Then click on +Organization link, you would get:

![organization-creation-1](/static/site_app/help/organization-creation-1.png)

Type your new organizatio name then click Create.

### Timelines

Timelines are great for sharing information, storing notes regarding a project and even delegating simple tasks.
Timelines can be used as super backlogs when deaing with Scrum Methodology. As posts can be forked into cards
it allows one to setup a timeline to be used as a scrum board backlog.

### Timeline Creation

For creating a timeline just click on Home at the navbar then on the wrench icon at the organization
toolbar:

![timeline-creation-0](/static/site_app/help/timeline-creation-0.png)

You would get:

![timeline-creation-1](/static/site_app/help/timeline-creation-1.png)

Notice that you can associate timelines to a given project by setting up a common slug.
You could fill the above fields with:

**Name:** Notes

**Description:** Arcamens/

Or you could do:

**Name:** Arcamens/Notes

**Description:** Notes on arcamens project.

There are many ways of grouping boards and timelines, feel free to pick up the
best one for you. You don't need to pick a description for your boards/timelines at all.

**See:** Collection Filters

After filling the fields you would get your timeline being listed altogether with your boards.

### Posts

Timeline posts can be used for multiple purposes, they can convey information about events,
tasks and even play a nice role as project notes. Snippets can be attached to posts, a snippet
can contain a title and markdown content. 

Tasks that demand one to collect information regarding a given subject can be delegated by using posts. 
The person attaches the missing information to the post as a snippet.

![post-0](/static/site_app/help/post-0.png)

Some tasks arent directly related to a specific project these tasks
can be delegated to a team or user by using a post.

![post-1](/static/site_app/help/post-1.png)

### Post Creation

After a timeline is created just access it then click on +Post at the timeline toolbar:

![post-creation-0](/static/site_app/help/post-creation-0.png)

You would get:

![post-creation-1](/static/site_app/help/post-creation-1.png)

Posts can have a short title that holds a description of the post content and
a markdown content.

After pressing Create the post will be created and every timeline user will get notified
of the post creation.

### Post Edition

### Post Workers

You can mention peers on a post, assign them to execute some task that's described over a timeline post.
A post becomes a task when there is at least a worker that is assigned to it.

Click on the Assign entry at the post toolbar in order to assign it to someone:

![post-workers-0](/static/site_app/help/post-workers-0.png)

Then you would get:

![post-workers-1](/static/site_app/help/post-workers-1.png)

Once you bind/unbind a worker to a post then the worker gets notified of it.
The worker name will be listed on the post.

### Post Tags

It is possible to tag posts for quickly finding information that is related to a given subject. Tagging a post
is as simple as tagging a card. After the post is tagged then an event is fired to all timeline users
and post workers.

Click on Tags entry at the post toolbar:

![post-tags-0](/static/site_app/help/post-tags-0.png)

Then you would get:

![post-tags-1](/static/site_app/help/post-tags-1.png)

### Organization Invites

An organization can contain as many users as your account plan allows. Users are invited to an organization
through e-mail. When the user is already an arcamens user then it is enough to click on the link that was sent
then join the organization. In the case his e-mail isn't belonging to an arcamens account then he will have to fill
a quick form in order to join the invite organization.

In order to send an invite just click Home at the navbar then go to the organization menu and click on the
wrench icon:

![organization-invites-0](/static/site_app/help/organization-invites-0.png)

Click on Members then you get;

![organization-invites-1](/static/site_app/help/organization-invites-1.png)

Which would list all your organization members.

Click on the plus sign at the top:

![organization-invites-2](/static/site_app/help/organization-invites-2.png)

Then fill the field with the peer e-mail to whom you would like to join your organization.

![organization-invites-3](/static/site_app/help/organization-invites-3.png)

You can check all invites that were sent by clicking on:

![organization-invites-4](/static/site_app/help/organization-invites-4.png)

You would have listed all invites:

![organization-invites-5](/static/site_app/help/organization-invites-5.png)

You can cancel invites or just resend the invite link. Notice that your account invites
can't override your account max users limit. The invites sum up with regular users and should
be lesser or equal your account max users limit.

### Organization Admins

### Timeline Members

Users of a timeline get notification from all events that happen with the timeline. Whenever an user
is binded/unbinded to a timeline everyone who is in the timeline gets notified.

For binding/unbinding users to a timeline just access the timeline then:

![timeline-members-0](/static/site_app/help/timeline-members-0.png)

Then you would get:

![timeline-members-1](/static/site_app/help/timeline-members-1.png)

From there you can search users from your organization that match a given criterea.

**See:** [Advanced User Search](#advanced-user-search)


### Post E-mail/Notifications

When a post has workers who were assigned it may be interesting to call attention
of these workers through e-mail. A link for the post would be sent through e-mail
with a message.

![post-email-notification-0](/static/site_app/help/post-email-notification-0.png)

You can click on the worker name and then:

![post-email-notification-1](/static/site_app/help/post-email-notification-1.png)

After clicking on Request attention through e-mail you would be prompted with:

![post-email-notification-2](/static/site_app/help/post-email-notification-2.png)

Fill the form and send the e-mail notification.

You can as well send notification to all post workers by clicking on Alert Workers.

### Post Search

The post search mechanism allows to search through all posts that you have access regardless
if it has a worker or not. For such just click on the Post link at the navbar:

![post-search-0](/static/site_app/help/post-search-0.png)

Then you would get:

![post-search-1](/static/site_app/help/post-search-1.png)

**Examples:**

Would find all posts where the three strings show up either in the label or markdown:

    bug + engine + wheels


Would find all posts where the strings 'bug' or 'engine wheels' show up.


    bug + engine wheels


Leave the **Done** field checked to search only through archived posts.

### Search for Post Tasks

When a post is created and it is assigned to someone then it becomes a task.
It is possible to search for archived or active tasks by clicking at the Tasks/Posts link
at the navbar:

![search-for-post-tasks-0](/static/site_app/help/search-for-post-tasks-0.png)

Then you would get:

![search-for-post-tasks-1](/static/site_app/help/search-for-post-tasks-1.png)

The option **Assigned to me** would perform the search pattern through
all tasks that someone has assigned to you even if it was assigned by yourself.

If you option for  **Created by me** then it would check the pattern against all posts
that you created and it was at least one worker binded to.

In the above example it matches all cards that you are assigned to and contains
the strings 'snippet', 'form', 'html'.

Notice that the order of strings is not relevant; You could also try:

~~~
need a snippet + form + html
~~~

Which would work alike.

**Note:** Leave the Done attribute checked for searching only through the archived posts.

### Event Comments

All kind of user actions in Arcamens are liable of being commented. Whenever an user
assigns a worker to a post it generates an event then the event/action can be commented out.

When an user action is commented then another event is generated but it doesn't allow
comments for action comments.

Click on Events at the navbar:

![event-comments-0](/static/site_app/help/event-comments-0.png)

Then you would get:

![event-comments-1](/static/site_app/help/event-comments-1.png)

By clicking on the event Comments link:

![event-comments-2](/static/site_app/help/event-comments-2.png)


The users who are related to the event would get a new event like:

![event-comments-3](/static/site_app/help/event-comments-3.png)

They can reply by clicking on the event Comments link.

### Post Filter

It is possible to filter timeline posts as well, whenever you access the timeline
then it will list just posts that match the filter pattern.

For such just access the timeline then click on Filter at the timeline menu:

![post-filter-0](/static/site_app/help/post-filter-0.png)

You would get:

![post-filter-1](/static/site_app/help/post-filter-1.png)

It is mostly useful for filtering posts based on tag, owner or workers but it works
with simple patterns as well.

Would list all posts that have both tags.

    tag:feature + tag:bug

    
Would list all posts whose owner's email or name matches the string 'last.src':


    owner:last.src


Listing posts that has a specific worker:


    worker:last.src


Would list all posts that have two workers whose name/email matches both strings.

    worker:last.src + worker:porton


**See:** [Advanced Post Search](#advanced-post-search)

### Collection Filter

Timelines and boards can be grouped by subject/project, it allows to form collections of boards/timelines.
One could have a project that has many plugins and keep a board for each one of its plugins.

It is necessary to stabilish a naming convention for your boards/timelines. 

For example:

    Timeline: Arcamens/Notes

    Board: Arcamens

    Timeline: Arcamens/News

    Timeline: Arcamens/Bugs


All these objects have a common pattern in its name. As arcamens allows to setup filter for boards/timelines 
then if you want to view just boards or timelines that are related to a given subject it gets simple.

Just click Home at the navbar and click on the Filter link at the organization menu:

![collection-filter-0](/static/site_app/help/collection-filter-0.png)

You would get:

![collection-filter-1](/static/site_app/help/collection-filter-1.png)

In the previously stated context if you typed the string 'Arcamens' then you would view
all the boards/timelines that contain such a string either in its name or description.

### Card Colors

When a card is a task it displays as green:

![card-colors-0](/static/site_app/help/card-colors-0.png)

When a card is assigned to you then it displays as red:

![card-colors-1](/static/site_app/help/card-colors-1.png)

A card fork's background is lighter than the usual card as well:

![card-colors-2](/static/site_app/help/card-colors-2.png)

### Card E-mail/Notifications

When a card is created and it has workers bound then it is possible to send
e-mail notifications to the card workers.

For such just access the card then click on the card worker name:

![card-email-notification-0](/static/site_app/help/card-email-notification-0.png)

You'll get:

![card-email-notification-1](/static/site_app/help/card-email-notification-1.png)

After clicking on **Request Attention through e-mail** you would get:

![card-email-notification-2](/static/site_app/help/card-email-notification-2.png)

You can fill with some message to be sent to the user.

When the card has many workers you can just click on the **Alert workers?** link
then sending an alert to all card workers at once.

### Card Filter

You can specify a pattern for filtering cards inside lists as well thus allowing one to view just cards
that have attributes matching requirements.

Access the desired list then click on Filter at the list menu:

![card-filter-0](/static/site_app/help/card-filter-0.png)

You would get:

![card-filter-1](/static/site_app/help/card-filter-1.png)

You can filter by tag, worker, owner etc.

**See:** [Advanced Card Search](#advanced-card-search)

### Card Relations

### Card Forks

When a given task can't be executed at once then it is necessary
to break it into multiple subtasks. In Arcamens it is named card forking, 
when you fork a card you create a link between both cards.

Consider the card below:

![card-forks-0](/static/site_app/help/card-forks-0.png)

In order to fork such a card just click on : Fork/Card link then you would get:

![card-forks-1](/static/site_app/help/card-forks-1.png)

When there are many lists you can just filter the lists based on a pattern:

![card-forks-2](/static/site_app/help/card-forks-2.png)

**Note:** If you wanted to search for a list named "beta" that is in a board named "alpha"
then you could do:

~~~
alpha + beta
~~~

Notice that if you inserted just the list name it would output more results if you have other lists named like this. 
It is also important to notice that the above pattern would match all lists that either board name
or list name contains each one of the strings "alpha" and "beta". 

For more consistent results just use:

~~~
board:alpha + name:beta
~~~

It would make sure to list just a list from a board that contains the string "alpha" in its name
and the list name contains the string "beta".

Once you pick up the desired list you will get the fork creation dialog:

![card-forks-3](/static/site_app/help/card-forks-3.png)

If you click on **Keep old content** link it will fill the fields with the parent card
attributes. It is useful sometimes when you just want to fork and edit the previous task.

After forking you'll get:

![card-forks-4](/static/site_app/help/card-forks-4.png)

You can browse all forks and parents of a given card by following the
links on the card.

**Note:** You can open a given card in a new browser tab by just right clicking it then open in a new tab.

**See:** [Advanced List Search](#advanced-list-search)


### Post Forks

Timeline posts can be forked into cards, it is mostly useful when a timeline is used
as a kanban board backlog. 

Timelines are great for sharing information of all kind, one might use a timeline
to get bug reports and fork the bug reports into card tasks over their
corresponding project boards. It all depends on how you feel more comfortable
to model your team workflow. 

For forking a post just access the post:

![post-forks-0](/static/site_app/help/post-forks-0.png)

After that just click on: Fork/Card it would give you:

![post-forks-1](/static/site_app/help/post-forks-1.png)

For basic understanding on how to filter lists:

**See:** [Card Forks](#card-forks)

After picking up the desired list you would get:

![post-forks-2](/static/site_app/help/post-forks-2.png)

After creating the card then everyone who is attached to the timeline
and to the destin list's board will get notified of the fork creation.

Some features that should be implemented may be related to multiple project boards, 
the forking mechanism allows a fancy approach for keeping track of all tasks
that are necessary in order to have a given feature implemented.

For a more complete reference on list filters:

**See:** [Advanced List Search](#advanced-list-search)

### Advanced User Search

You can search users for attributes like name, e-mail or tags.

    tag:developer
 

Would list all organization users who were tagged with developer. You can combine tags as well.


    tag:developer + tag:python 


You can combine tags but mix them with other kind of attributes like name or email.


    tag:dev + @arcamens.com

Would list all workers that were tagged as developer and the email matches @arcamens.com.


![advanced-user-search-0](/static/site_app/help/advanced-user-search-0.png)

Notice that if you did:


    tag:dev + oliveira


It would list all users with the tag dev and have the string oliveira
appearing either in the name or email attributes. When you want to limit the
search to be performed under a given attribute like email you could do:


    tag:dev + email:oliveira

### Advanced Card Search

### Advanced Post Search

### Advanced List Search

When forking cards/posts it is necessary to search the desired
board list that will contain the fork. Lists are searched pretty much
like cards/posts except that it contains some different attributes.

List attributes used in searches:

**owner**

The one who has created the list.

**name**

The name of the list.

**board**

The board that contains the list.

**description**

The list description.

When no attribute is specified then the default attributes
that are assumed consist of the board name and list name.

For example:

~~~
arcamens + todo
~~~

The above pattern would match all lists that contains
each one of the strings either in the board name or list name.
So, if there were a list named Todo in a board named Arcamens
then it would be listed.

Suppose you wanted to list all lists whose owner is a guy named iury and
it is named Todo:


~~~
owner:iury + name:todo
~~~

**Note:** When the owner attribute is used then it matches against the owner name and e-mail.

If you wanted to search all lists based on description then you could do:

~~~
description:contain bugs
~~~

It would list all lists that contains the string 'contain bugs' in its description.
When searching by using the description attribute it is mostly useful if you have
a project with many plugins and you're handling all your plugins insde the project board.

The naming scheme examplifies the situation:

~~~
Arcamens
    Name:Todo
    Description:core_app
    .
    .
    .

    Name:Todo
    Description:bitbucket_app

    Doing
    Description:bitbucket_app

    Done
    Description:bitbucket_app

    To check
    Description:bitbucket_app


    .
    .
    .
~~~

Imagine you wanted to fork a given card from core_app/Todo list
into bitbucket_app/Todo list:

~~~
arcamens + description:bitbucket
~~~

That would be enough to list all lists from board arcamens whose description
contains the slug string 'bitbucket'.

You could as well do:

~~~
board:arcamens + description:bitbucket
~~~

Which would give you more accurate results in case you have other boards where the string
'arcamens' shows in.

### Timeline Settings/Removal

You can rename a timeline or delete it, you just access the desired timeline
then click on Settings at the timeline menu:

![timeline-settings-0](/static/site_app/help/timeline-settings-0.png)

You would get:

![timeline-settings-1](/static/site_app/help/timeline-settings-1.png)

From there you can change the timeline attributes like name/description.

You can as well click on Delete then you'll be asked for confirmation. 
Type the timeline name then press Delete.

### Board Settings/Removal

You can rename a board by accessing its settings form. For such just access the board
then click on the wrench icon:

![board-settings-0](/static/site_app/help/board-settings-0.png)

Click on Settings then you get:

![board-settings-1](/static/site_app/help/board-settings-1.png)

From there you can as well delete the board, you'll be asked for confirmation.

### Bitbucket Integration

### Organization User Removal

In order to remove an user from an organization it is necessary to be admin of the organization.
The one who is removing the user will own all timeliens and boards of the removed user.

Click on the wrench icon at the organization menu:

![organization-user-removal-0](/static/site_app/help/organization-user-removal-0.png)

Then click on Members, you would get:

![organization-user-removal-1](/static/site_app/help/organization-user-removal-1.png)

### Organization Settings/Removal

Click on wrench icon at the organization menu then Settings:

![organization-settings-removal-0](/static/site_app/help/organization-settings-removal-0.png)

You would get:

![organization-settings-removal-1](/static/site_app/help/organization-settings-removal-1.png)

### Logs














