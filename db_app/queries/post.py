SELECT_ALL_POSTS_BY_FORUM_UNSPECIFIED = u'''
                                SELECT date, dislikes, forum,
                                      id, isApproved, isDeleted, isEdited,
                                      isHighlighted, isSpam, likes, message, parent,
                                      likes - dislikes as points, thread, user
                                FROM Posts
                                WHERE forum = %s
                                '''


SELECT_ALL_POSTS_BY_USER_EMAIL_UNSPECIFIED = u'''
                                SELECT date, dislikes, forum,
                                      id, isApproved, isDeleted, isEdited,
                                      isHighlighted, isSpam, likes, message, parent,
                                      likes - dislikes as points, thread, user
                                FROM Posts
                                WHERE user = %s
                                '''

SELECT_POSTS_BY_FORUM_OR_THREAD_UNSPECIFIED = u'''
                                    SELECT date, dislikes, forum, id,
                                            isApproved, isDeleted, isEdited, isHighlighted,
                                            isSpam, likes, message, parent,
                                            likes - dislikes as points, thread, user
                                    FROM Posts WHERE {} = %s
                                  '''


INSERT_POST = u'''INSERT INTO Posts
                  (date, message, user, forum, thread)
                  VALUES
                  (%s, %s, %s, %s, %s);
               '''


SELECT_POST_DATA_BY_ID = u''' SELECT date, dislikes, forum, id,
                                    isApproved, isDeleted, isEdited, isHighlighted,
                                    isSpam, likes, message, parent,
                                    likes - dislikes as points, thread, user
                             FROM Posts
                             WHERE id = %s;
                        '''

SELECT_DELETED_FLAG_BY_ID = u'''
                                SELECT isDeleted FROM Posts
                                WHERE id = %s
                            '''

# SELECT_PARENT_POST_HIERARCHY = u'''SELECT id, child_posts_count, hierarchy_id FROM Posts
#                                   WHERE id = %s;
#                                '''
#
# UPDATE_CHILD_POST_COUNT = u'''UPDATE post
#                              SET child_posts_count = child_posts_count + 1
#                              WHERE id = %s;
#                           '''
#
# SELECT_TOP_POST_NUMBER = u'''SELECT head_posts_number
#                             FROM post_hierarchy_utils
#                             WHERE thread_id = %s;
#                         '''
#
# INSERT_TOP_POST_NUMBER = u'''INSERT INTO post_hierarchy_utils
#                              (thread_id, head_posts_number)
#                              VALUES
#                              (%s, 1);
#                           '''
#
# UPDATE_POST_NUMBER = u'''UPDATE post_hierarchy_utils
#                         SET head_posts_number = head_posts_number + 1
#                         WHERE thread_id = %s;
#                      '''

UPDATE_POST_DELETE_FLAG = u'''UPDATE Posts
                                 SET isDeleted = {}
                                 WHERE id = %s;
                               '''

SELECT_POST_BY_ID = u'''
                        SELECT id FROM Posts
                        WHERE id = %s ;
                    '''

UPDATE_POST_MESSAGE_BY_ID = u'''
                            UPDATE Posts
                            SET message = %s
                            WHERE id = %s
                            '''

UPDATE_POST_VOTES = u'''UPDATE Posts
                       SET {} = {} + 1
                       WHERE id= %s
                    '''

SELECT_ALL_POSTS_BY_THREAD = u'''SELECT date, dislikes, forum,
                                      id, isApproved, isDeleted, isEdited,
                                      isHighlighted, isSpam, likes, message, parent,
                                      likes - dislikes as points, thread, user
                                FROM Posts
                                WHERE thread = %s
                            '''

