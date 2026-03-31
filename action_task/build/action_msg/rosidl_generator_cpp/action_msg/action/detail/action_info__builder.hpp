// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from action_msg:action/ActionInfo.idl
// generated code does not contain a copyright notice

#ifndef ACTION_MSG__ACTION__DETAIL__ACTION_INFO__BUILDER_HPP_
#define ACTION_MSG__ACTION__DETAIL__ACTION_INFO__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "action_msg/action/detail/action_info__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace action_msg
{

namespace action
{

namespace builder
{

class Init_ActionInfo_Goal_target
{
public:
  Init_ActionInfo_Goal_target()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::action_msg::action::ActionInfo_Goal target(::action_msg::action::ActionInfo_Goal::_target_type arg)
  {
    msg_.target = std::move(arg);
    return std::move(msg_);
  }

private:
  ::action_msg::action::ActionInfo_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::action_msg::action::ActionInfo_Goal>()
{
  return action_msg::action::builder::Init_ActionInfo_Goal_target();
}

}  // namespace action_msg


namespace action_msg
{

namespace action
{

namespace builder
{

class Init_ActionInfo_Result_final_count
{
public:
  Init_ActionInfo_Result_final_count()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::action_msg::action::ActionInfo_Result final_count(::action_msg::action::ActionInfo_Result::_final_count_type arg)
  {
    msg_.final_count = std::move(arg);
    return std::move(msg_);
  }

private:
  ::action_msg::action::ActionInfo_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::action_msg::action::ActionInfo_Result>()
{
  return action_msg::action::builder::Init_ActionInfo_Result_final_count();
}

}  // namespace action_msg


namespace action_msg
{

namespace action
{

namespace builder
{

class Init_ActionInfo_Feedback_current_count
{
public:
  Init_ActionInfo_Feedback_current_count()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::action_msg::action::ActionInfo_Feedback current_count(::action_msg::action::ActionInfo_Feedback::_current_count_type arg)
  {
    msg_.current_count = std::move(arg);
    return std::move(msg_);
  }

private:
  ::action_msg::action::ActionInfo_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::action_msg::action::ActionInfo_Feedback>()
{
  return action_msg::action::builder::Init_ActionInfo_Feedback_current_count();
}

}  // namespace action_msg


namespace action_msg
{

namespace action
{

namespace builder
{

class Init_ActionInfo_SendGoal_Request_goal
{
public:
  explicit Init_ActionInfo_SendGoal_Request_goal(::action_msg::action::ActionInfo_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::action_msg::action::ActionInfo_SendGoal_Request goal(::action_msg::action::ActionInfo_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::action_msg::action::ActionInfo_SendGoal_Request msg_;
};

class Init_ActionInfo_SendGoal_Request_goal_id
{
public:
  Init_ActionInfo_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ActionInfo_SendGoal_Request_goal goal_id(::action_msg::action::ActionInfo_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_ActionInfo_SendGoal_Request_goal(msg_);
  }

private:
  ::action_msg::action::ActionInfo_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::action_msg::action::ActionInfo_SendGoal_Request>()
{
  return action_msg::action::builder::Init_ActionInfo_SendGoal_Request_goal_id();
}

}  // namespace action_msg


namespace action_msg
{

namespace action
{

namespace builder
{

class Init_ActionInfo_SendGoal_Response_stamp
{
public:
  explicit Init_ActionInfo_SendGoal_Response_stamp(::action_msg::action::ActionInfo_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::action_msg::action::ActionInfo_SendGoal_Response stamp(::action_msg::action::ActionInfo_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::action_msg::action::ActionInfo_SendGoal_Response msg_;
};

class Init_ActionInfo_SendGoal_Response_accepted
{
public:
  Init_ActionInfo_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ActionInfo_SendGoal_Response_stamp accepted(::action_msg::action::ActionInfo_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_ActionInfo_SendGoal_Response_stamp(msg_);
  }

private:
  ::action_msg::action::ActionInfo_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::action_msg::action::ActionInfo_SendGoal_Response>()
{
  return action_msg::action::builder::Init_ActionInfo_SendGoal_Response_accepted();
}

}  // namespace action_msg


namespace action_msg
{

namespace action
{

namespace builder
{

class Init_ActionInfo_GetResult_Request_goal_id
{
public:
  Init_ActionInfo_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::action_msg::action::ActionInfo_GetResult_Request goal_id(::action_msg::action::ActionInfo_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::action_msg::action::ActionInfo_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::action_msg::action::ActionInfo_GetResult_Request>()
{
  return action_msg::action::builder::Init_ActionInfo_GetResult_Request_goal_id();
}

}  // namespace action_msg


namespace action_msg
{

namespace action
{

namespace builder
{

class Init_ActionInfo_GetResult_Response_result
{
public:
  explicit Init_ActionInfo_GetResult_Response_result(::action_msg::action::ActionInfo_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::action_msg::action::ActionInfo_GetResult_Response result(::action_msg::action::ActionInfo_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::action_msg::action::ActionInfo_GetResult_Response msg_;
};

class Init_ActionInfo_GetResult_Response_status
{
public:
  Init_ActionInfo_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ActionInfo_GetResult_Response_result status(::action_msg::action::ActionInfo_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_ActionInfo_GetResult_Response_result(msg_);
  }

private:
  ::action_msg::action::ActionInfo_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::action_msg::action::ActionInfo_GetResult_Response>()
{
  return action_msg::action::builder::Init_ActionInfo_GetResult_Response_status();
}

}  // namespace action_msg


namespace action_msg
{

namespace action
{

namespace builder
{

class Init_ActionInfo_FeedbackMessage_feedback
{
public:
  explicit Init_ActionInfo_FeedbackMessage_feedback(::action_msg::action::ActionInfo_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::action_msg::action::ActionInfo_FeedbackMessage feedback(::action_msg::action::ActionInfo_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::action_msg::action::ActionInfo_FeedbackMessage msg_;
};

class Init_ActionInfo_FeedbackMessage_goal_id
{
public:
  Init_ActionInfo_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ActionInfo_FeedbackMessage_feedback goal_id(::action_msg::action::ActionInfo_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_ActionInfo_FeedbackMessage_feedback(msg_);
  }

private:
  ::action_msg::action::ActionInfo_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::action_msg::action::ActionInfo_FeedbackMessage>()
{
  return action_msg::action::builder::Init_ActionInfo_FeedbackMessage_goal_id();
}

}  // namespace action_msg

#endif  // ACTION_MSG__ACTION__DETAIL__ACTION_INFO__BUILDER_HPP_
